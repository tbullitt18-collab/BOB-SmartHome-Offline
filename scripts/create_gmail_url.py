import urllib.parse

subject = "Mitigating Cold-Load Pickup & Transformer Inrush on Feeder Restorations (Pilot Proposal)"

body = """Hi Team,

When storm blackouts hit, simultaneous compressor and motor restarts during feeder re-energization ("cold-load pickup") create massive current surges that routinely blow substation transformers ($800k–$2.5M replacement costs + 6-month lead times).

Standard cloud-based demand response fails during these events because cellular towers and fiber backhauls are offline.

We developed BOB, an edge-native grid governor that coordinates residential and commercial load re-engagement 100% locally with zero cloud or cellular dependency. In our 50-home substation feeder benchmark simulations, BOB achieved:

• -78.0% Peak Inrush Current Reduction (dropped from 1,850 kW down to 406.1 kW).
• Zero Breaker Trips: Kept transformer loading at 42.7% thermal capacity, preventing secondary cascading blackouts.
• 100% Autonomous Offline Execution: Enforces deterministic, staggered re-energization directly at the edge panel.

We have packaged a turnkey 90-day, 50-gateway feeder pilot program ($45,000 flat) to validate this on an active feeder circuit.

You can inspect our full engineering benchmark curves, IEEE 1547 metrics, and open-source architecture here:
https://github.com/tbullitt18-collab/BOB-SmartHome-Offline/blob/main/commercial/utilities-grid/BENCHMARK_RESULTS.md

Would you have 15 minutes this week to review the load curves?

Best regards,
Todd Bullitt
Founder & Lead Architect, BOB Edge Systems
https://github.com/tbullitt18-collab/BOB-SmartHome-Offline
"""

to_list = "DEED@publicpower.org, incubatenergy@epri.com"
params = {
    "view": "cm",
    "fs": "1",
    "to": to_list,
    "su": subject,
    "body": body
}
gmail_url = "https://mail.google.com/mail/?" + urllib.parse.urlencode(params)

with open("gmail_url.txt", "w", encoding="utf-8") as f:
    f.write(gmail_url)

print("URL generated successfully.")
