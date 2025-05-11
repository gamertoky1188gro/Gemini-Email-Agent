from gemini_agent import select_model, ask_loop, cleanup_prompt
from email_loader import load_emails_from_temp

def main():
    print("== Gemini Email Agent ==")
    model_info = select_model()
    print(f"\n[+] Selected model: {model_info['name']}")

    emails = load_emails_from_temp()
    if not emails:
        print("[!] No emails loaded. Exiting.")
        return

    ask_loop(model_info['id'], emails)
    cleanup_prompt()

if __name__ == "__main__":
    main()
