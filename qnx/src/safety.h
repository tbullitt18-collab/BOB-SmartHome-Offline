#ifndef ASCE_SAFETY_H
#define ASCE_SAFETY_H

#define EPA_MIN_PSI          20.0  /* EPA / Ten States minimum distribution pressure */
#define DESIGN_MARGIN_PSI     5.0  /* arbiter targets >= 25 PSI */
#define BREAKER_LIMIT_AMPS   50.0  /* service breaker limit for inrush planning */
#define STAGGER_MS          500u

enum { LOAD_BOOSTER_PUMP = 0, LOAD_HVAC = 1, LOAD_LIGHTING = 2, LOAD_MEDICAL_O2 = 3, NUM_LOADS = 4 };

typedef enum { MSG_HYDRAULIC = 1, MSG_START_LOADS = 2, MSG_SHED_LOAD = 3, MSG_SHUTDOWN = 9 } msg_type_t;
typedef enum { DEC_APPROVED = 0, DEC_APPROVED_MODIFIED = 1, DEC_REJECTED = 2 } decision_t;
typedef enum {
    R_OK = 0, R_BYPASS_ADDED = 1, R_NO_SAFE_BYPASS = 2,
    R_STAGGERED = 3, R_FIREWALL_PROTECTED = 4, R_BAD_REQUEST = 5
} reason_t;

typedef struct {
    int      type;
    unsigned seq;
    double   bypass_pct;     /* MSG_HYDRAULIC: requested bypass opening */
    unsigned load_mask;      /* MSG_START_LOADS: bitmask of loads to start */
    int      load_id;        /* MSG_SHED_LOAD */
    int      execute_delays; /* 1 = actually sleep stagger delays (demo), 0 = plan only (benchmark) */
} safety_req_t;

typedef struct {
    int      decision;
    int      reason;
    double   predicted_psi;
    double   applied_bypass_pct;
    double   peak_amps;
    int      stagger_steps;
    unsigned stagger_ms;
    char     receipt[65];
} safety_rep_t;

typedef struct { const char *name; double run_amps; double inrush_amps; int protected_load; } load_t;
extern const load_t LOADS[NUM_LOADS];

/* Reduced-order hydraulic model: downstream (St. Jude, J-42) pressure after isolating P-4. */
double hydraulic_predict_psi(double bypass_pct);

const char *decision_str(int d);
const char *reason_str(int r);

#endif
