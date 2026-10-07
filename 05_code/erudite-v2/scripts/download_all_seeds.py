import requests
import os
import sys

folders = [
    "/home/realsamkarim/docrag-v2/erudite-v2/seed_docs/statutes",
    "/home/realsamkarim/docrag-v2/erudite-v2/seed_docs/it_security",
    "/home/realsamkarim/docrag-v2/erudite-v2/seed_docs/clinical_safety"
]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

it_security_urls = [
    "https://www.hud.ac.uk/media/policydocuments/IT-Security-Policy.pdf"
]

clinical_safety_urls = [
    "https://database.ich.org/sites/default/files/E6_R2_Addendum.pdf"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

# Download IT Security
it_success = False
it_path = "/home/realsamkarim/docrag-v2/erudite-v2/seed_docs/it_security/it_security_policy.pdf"
for url in it_security_urls:
    print(f"Trying IT security download from: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200 and response.content.startswith(b"%PDF"):
            with open(it_path, "wb") as f:
                f.write(response.content)
            print(f"  SUCCESS! Saved IT Security PDF to {it_path}")
            it_success = True
            break
    except Exception as e:
        print("  Failed:", e)

# Download Clinical Safety
clinical_success = False
clinical_path = "/home/realsamkarim/docrag-v2/erudite-v2/seed_docs/clinical_safety/clinical_trials_guideline.pdf"
for url in clinical_safety_urls:
    print(f"Trying Clinical safety download from: {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200 and response.content.startswith(b"%PDF"):
            with open(clinical_path, "wb") as f:
                f.write(response.content)
            print(f"  SUCCESS! Saved Clinical Safety PDF to {clinical_path}")
            clinical_success = True
            break
    except Exception as e:
        print("  Failed:", e)

if not it_success or not clinical_success:
    print("\nCRITICAL ERROR: One or more domain seed downloads failed completely!")
    sys.exit(1)

print("\nAll premium multi-domain seed files downloaded successfully!")
