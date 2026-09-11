import urllib.parse

to_email = "rmathur@redhat.com"
subject = "Re: Red Hat Partner Application - ASCE Technologies, LLC"

body = """Dear Rahul,

Thank you for following up.

ASCE Technologies, LLC is a technology development firm registered in Georgia, USA. Our root web domain (https://ascetech.org) hosts our public sector navigational tools, while our enterprise software division—BOB Edge Systems—manages our edge automation and OpenShift disaster-resilience product line.

We have published our official enterprise technology showcase and company verification page on our domain at:
👉 https://ascetech.org/technology

To review our full open-source architecture, engineering benchmarks, and OpenShift operator bundle submitted for the Red Hat Ecosystem Catalog, please refer to our primary software repository:
• Corporate Repository & OpenShift Operator Suite:
  https://github.com/tbullitt18-collab/BOB-SmartHome-Offline

• Verified Business Details:
  - Legal Entity Name: ASCE Technologies, LLC
  - Technology Portal: https://ascetech.org/technology
  - Business Email: t.bullitt@ascetech.org
  - Primary Contact: Todd Bullitt, Managing Director & Founder
  - State of Registration: Georgia, United States
  - Product Line: BOB Edge Automation & Disaster Resilience Platform (bob-edge-operator)

If you require our Georgia Secretary of State registration certificate, W-9, or EIN documentation to complete the partner review, please let me know and I will provide them immediately.

Thank you for updating the application and continuing the partner-review process.

Sincerely,

Todd Bullitt
Managing Director & Founder
ASCE Technologies, LLC
t.bullitt@ascetech.org
https://ascetech.org
"""

params = {
    "view": "cm",
    "fs": "1",
    "to": to_email,
    "su": subject,
    "body": body
}

gmail_url = "https://mail.google.com/mail/?" + urllib.parse.urlencode(params)
mailto_url = f"mailto:{to_email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

print(f"Gmail URL: {gmail_url}")
print(f"\nMailto URL: {mailto_url}")

with open("redhat_reply_links.txt", "w", encoding="utf-8") as f:
    f.write(f"GMAIL_URL:\n{gmail_url}\n\nMAILTO_URL:\n{mailto_url}\n")



