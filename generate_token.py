from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def main():
    with open("credentials.json", "r") as f:
        creds_info = json.load(f)['web']

    flow = Flow.from_client_config(
        {"web": creds_info},
        scopes=SCOPES,
        redirect_uri="http://localhost:3000/"
    )

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    print("Open the following URL in your browser:")
    print(auth_url)

    code = input("Paste the authorization code here: ")
    flow.fetch_token(code=code)
    creds = flow.credentials

    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())
    print("token.json generated successfully.")

    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    print(f"Authenticated as: {profile['emailAddress']}")

if __name__ == '__main__':
    main()
