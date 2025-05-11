import os
import json

def load_emails_from_temp(folder="temp"):
    emails = []
    if not os.path.exists(folder):
        print("[!] Temp folder not found.")
        return emails

    for file in os.listdir(folder):
        if file.endswith(".json"):
            path = os.path.join(folder, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    emails.append(data)
            except Exception as e:
                print(f"[!] Error reading {file}: {e}")
    print(f"[+] Loaded {len(emails)} emails from '{folder}'")
    return emails
