import os
import json
import argparse
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def decode_message(payload):
    if 'data' in payload.get('body', {}):
        raw_data = payload['body']['data']
        decoded_bytes = base64.urlsafe_b64decode(raw_data + '==')
        return decoded_bytes.decode('utf-8', errors='ignore')
    elif 'parts' in payload:
        parts = payload['parts']
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                raw_data = part['body'].get('data')
                if raw_data:
                    decoded_bytes = base64.urlsafe_b64decode(raw_data + '==')
                    return decoded_bytes.decode('utf-8', errors='ignore')
            elif part.get('mimeType') == 'text/html':
                raw_data = part['body'].get('data')
                if raw_data:
                    decoded_bytes = base64.urlsafe_b64decode(raw_data + '==')
                    return decoded_bytes.decode('utf-8', errors='ignore')
    return ""

def list_labels(service):
    results = service.users().labels().list(userId='me').execute()
    labels = [label['name'] for label in results.get('labels', [])]
    print("Labels:", labels)

def download_emails(service, max_results=None, showlog=False):
    os.makedirs('temp', exist_ok=True)
    all_messages = []
    next_page_token = None
    total_emails = 0

    # Fetch all labels
    labels_response = service.users().labels().list(userId='me').execute()
    labels = labels_response.get('labels', [])

    try:
        # Loop through all labels
        for label in labels:
            label_id = label['id']
            label_name = label['name']
            label_message_count = 0  # To count emails per label

            print(f"Fetching emails for label: {label_name}")

            # Fetch messages for this label with pagination
            while True:
                response = service.users().messages().list(
                    userId='me',
                    maxResults=min(max_results, 5000000) if max_results else 5000000,
                    labelIds=[label_id],
                    pageToken=next_page_token
                ).execute()

                messages = response.get('messages', [])
                all_messages.extend(messages)
                label_message_count += len(messages)

                # Check for the next page token
                next_page_token = response.get('nextPageToken', None)
                if not next_page_token or (max_results and len(all_messages) >= max_results):
                    break

            # Print total emails for this label
            print(f"Total emails for label {label_name}: {label_message_count}")
            total_emails += label_message_count

            # Stop if max_results is reached
            if max_results and len(all_messages) >= max_results:
                break

        # Print grand total emails
        if max_results:
            print(f"Grand total emails fetched: {total_emails}/{max_results}")
        else:
            print(f"Grand total emails fetched: {total_emails}")

        # Limit the number of emails if max_results is set
        if max_results:
            all_messages = all_messages[:max_results]

        for i, msg in enumerate(all_messages):
            msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            payload = msg_detail.get('payload', {})
            headers = payload.get('headers', [])

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
            from_ = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")
            to = next((h['value'] for h in headers if h['name'] == 'To'), "Unknown Recipient")
            date = next((h['value'] for h in headers if h['name'] == 'Date'), "Unknown Date")
            snippet = msg_detail.get('snippet', '')
            body = decode_message(payload)

            email_data = {
                'id': msg['id'],
                'subject': subject,
                'from': from_,
                'to': to,
                'date': date,
                'snippet': snippet,
                'body': body
            }

            with open(f'temp/email_{i+1}.json', 'w') as f:
                json.dump(email_data, f, indent=2)

            log_message = f"Downloaded email {i+1}: {subject} from {from_} to {to}\n"
            if showlog:
                print(log_message)
            yield log_message.encode("utf-8")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/download-emails':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data)

            max_results = params.get('max', None)
            showlog = params.get('showdownloadlog', False)

            try:
                service = authenticate_gmail()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Transfer-Encoding', 'chunked')
                self.end_headers()

                # Call the download_emails function and stream logs to the client
                for chunk in download_emails(service, max_results, showlog):
                    chunk_size = f"{len(chunk):X}\r\n".encode("utf-8")
                    self.wfile.write(chunk_size)
                    self.wfile.write(chunk)
                    self.wfile.write(b"\r\n")
                    self.wfile.flush()

                # Send the final chunk
                self.wfile.write(b"0\r\n\r\n")
            except Exception as e:
                error_message = f"Error: {str(e)}\n".encode("utf-8")
                chunk_size = f"{len(error_message):X}\r\n".encode("utf-8")
                self.wfile.write(chunk_size)
                self.wfile.write(error_message)
                self.wfile.write(b"\r\n")
                self.wfile.write(b"0\r\n\r\n")
        else:
            self.send_response(404)
            self.end_headers()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', default='no limit', help='Max number of emails to download')
    parser.add_argument('--showdownloadlog', default='false', help='Show download log')
    parser.add_argument('--server', default=None, help='Start server at specified port')
    args = parser.parse_args()

    max_results = None if args.max.lower() == 'no limit' or args.max.lower() == 'infinity' else int(args.max)
    showlog = args.showdownloadlog.lower() == 'true'

    if args.server:
        port = int(args.server)
        server = HTTPServer(('0.0.0.0', port), RequestHandler)
        print(f"Starting server on port {port}...")
        server.serve_forever()
    else:
        service = authenticate_gmail()
        list_labels(service)
        for log_message in download_emails(service, max_results, showlog):
            print(log_message.decode("utf-8"))

if __name__ == '__main__':
    main()
