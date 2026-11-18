#include "safety.h"
#include "sha256.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

const load_t LOADS[NUM_LOADS] = {
    { "booster_pump",          12.0, 32.0, 0 },
    { "hvac_compressor",       18.0, 48.0, 0 },
    { "non_critical_lighting",  4.0,  4.0, 0 },
    { "medical_oxygen_conc",    5.0,  5.0, 1 },
};

/*
 * Matches AquaPulse OS digital_twin.py (Millbrook baseline with P-4 isolated):
 *   RES-1 = 250.0 ft, P-1 loss = 1.2 ft, PUMP-1 (100% VFD) = +160.0 ft => PS-1 = 408.8 ft
 *   J-10 = 408.8 - 7.5 = 401.3 ft; J-30 = 401.3 - 5.8 = 395.5 ft; J-42 base = 385.5 ft (elev 160.0 ft)
 *   If P-4 closed and PRV-3 bypass == 0%: J-42 = 16.2 PSI (back-siphonage < 20.0 EPA rule).
 *   If P-4 closed and PRV-3 bypass > 0%: j42_head = 385.5 - 5.0 + 28.0 * (bypass_pct / 100.0)
 */
double hydraulic_predict_psi(double bypass_pct)
{
    if (bypass_pct <= 0.0) {
        return 16.2;
    }
    double prv3_open = bypass_pct / 100.0;
    if (prv3_open > 1.0) prv3_open = 1.0;
    double j42_head = (385.5 - 5.0) + (28.0 * prv3_open);
    return (j42_head - 160.0) * 0.4335;
}

const char *decision_str(int d)
{
    switch (d) {
        case DEC_APPROVED:          return "APPROVED";
        case DEC_APPROVED_MODIFIED: return "APPROVED_MODIFIED";
        case DEC_REJECTED:          return "REJECTED";
        default:                    return "UNKNOWN";
    }
}

const char *reason_str(int r)
{
    switch (r) {
        case R_OK:                 return "OK";
        case R_BYPASS_ADDED:       return "EPA_20_PSI_INTERLOCK_PRV3_BYPASS";
        case R_NO_SAFE_BYPASS:     return "NO_SAFE_BYPASS_FOUND";
        case R_STAGGERED:          return "NEC_INRUSH_STAGGER_ENFORCED";
        case R_FIREWALL_PROTECTED: return "LIFE_SAFETY_LOAD_PROTECTED";
        default:                   return "BAD_REQUEST";
    }
}

void compute_decision_receipt(const safety_req_t *req, const safety_rep_t *rep, char out[65])
{
    char buf[256];
    int n = snprintf(buf, sizeof(buf),
        "seq=%u|type=%d|dec=%d|rsn=%d|psi=%.2f|byp=%.1f|amps=%.2f|steps=%d",
        req->seq, req->type, rep->decision, rep->reason,
        rep->predicted_psi, rep->applied_bypass_pct,
        rep->peak_amps, rep->stagger_steps);
    if (n < 0) n = 0;
    if ((size_t)n >= sizeof(buf)) n = sizeof(buf) - 1;
    sha256_hex(buf, (size_t)n, out);
}

void evaluate_safety_request(const safety_req_t *req, safety_rep_t *rep)
{
    memset(rep, 0, sizeof(*rep));

    if (req->type == MSG_HYDRAULIC) {
        double req_byp = req->bypass_pct;
        double psi = hydraulic_predict_psi(req_byp);

        if (psi >= EPA_MIN_PSI) {
            rep->decision = DEC_APPROVED;
            rep->reason = R_OK;
            rep->applied_bypass_pct = req_byp;
            rep->predicted_psi = psi;
        } else {
            /* Deterministic barrier search for safe PRV-3 bypass >= EPA_MIN + margin */
            double safe_byp = 25.0;
            double safe_psi = hydraulic_predict_psi(safe_byp);
            while (safe_psi < (EPA_MIN_PSI + DESIGN_MARGIN_PSI) && safe_byp < 100.0) {
                safe_byp += 5.0;
                safe_psi = hydraulic_predict_psi(safe_byp);
            }
            if (safe_psi >= EPA_MIN_PSI) {
                rep->decision = DEC_APPROVED_MODIFIED;
                rep->reason = R_BYPASS_ADDED;
                rep->applied_bypass_pct = safe_byp;
                rep->predicted_psi = safe_psi;
            } else {
                rep->decision = DEC_REJECTED;
                rep->reason = R_NO_SAFE_BYPASS;
                rep->applied_bypass_pct = 0.0;
                rep->predicted_psi = psi;
            }
        }
    } else if (req->type == MSG_START_LOADS) {
        double simultaneous_peak = 0.0;
        double running_total = 0.0;
        double worst_staggered_peak = 0.0;
        int steps = 0;

        for (int i = 0; i < NUM_LOADS; i++) {
            if (req->load_mask & (1u << i)) {
                simultaneous_peak += LOADS[i].inrush_amps;
            }
        }

        if (simultaneous_peak <= BREAKER_LIMIT_AMPS) {
            rep->decision = DEC_APPROVED;
            rep->reason = R_OK;
            rep->peak_amps = simultaneous_peak;
            rep->stagger_steps = 1;
            rep->stagger_ms = 0;
        } else {
            /*
             * Order selected loads by descending (inrush - run) excess so the largest
             * transient spike runs first while steady-state baseline is lowest.
             */
            int order[NUM_LOADS];
            for (int i = 0; i < NUM_LOADS; i++) {
                if (req->load_mask & (1u << i)) order[steps++] = i;
            }
            for (int a = 0; a < steps; a++) {
                for (int b = a + 1; b < steps; b++) {
                    double ex_a = LOADS[order[a]].inrush_amps - LOADS[order[a]].run_amps;
                    double ex_b = LOADS[order[b]].inrush_amps - LOADS[order[b]].run_amps;
                    if (ex_b > ex_a) {
                        int tmp = order[a];
                        order[a] = order[b];
                        order[b] = tmp;
                    }
                }
            }
            for (int k = 0; k < steps; k++) {
                const load_t *ld = &LOADS[order[k]];
                double step_peak = running_total + ld->inrush_amps;
                if (step_peak > worst_staggered_peak) {
                    worst_staggered_peak = step_peak;
                }
                running_total += ld->run_amps;
            }
            if (worst_staggered_peak <= BREAKER_LIMIT_AMPS) {
                rep->decision = DEC_APPROVED_MODIFIED;
                rep->reason = R_STAGGERED;
            } else {
                rep->decision = DEC_REJECTED;
                rep->reason = R_STAGGERED;
            }
            rep->peak_amps = worst_staggered_peak;
            rep->stagger_steps = steps;
            rep->stagger_ms = (steps > 1) ? (unsigned)((steps - 1) * STAGGER_MS) : 0u;
        }
    } else if (req->type == MSG_SHED_LOAD) {
        if (req->load_id < 0 || req->load_id >= NUM_LOADS) {
            rep->decision = DEC_REJECTED;
            rep->reason = R_BAD_REQUEST;
        } else if (LOADS[req->load_id].protected_load) {
            rep->decision = DEC_REJECTED;
            rep->reason = R_FIREWALL_PROTECTED;
        } else {
            rep->decision = DEC_APPROVED;
            rep->reason = R_OK;
        }
    } else {
        rep->decision = DEC_REJECTED;
        rep->reason = R_BAD_REQUEST;
    }

    compute_decision_receipt(req, rep, rep->receipt);
}
