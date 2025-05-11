# Gemini Email Agent

The **Gemini Email Agent** is an advanced email analysis tool that integrates with Google's Gmail API and Google's Generative AI models. This project allows users to authenticate with their Gmail account, download and analyze emails, and ask questions about their email content using various Gemini AI models.

---

## Features

1. **Gmail Integration**: Authenticate with Gmail to fetch and process emails.
2. **Generative AI Models**: Utilize multiple Gemini AI models for email analysis and Q&A.
3. **Flask API**: Expose functionality via a RESTful API for external integrations.
4. **Email Management**: Download emails and store them locally as JSON files.
5. **Interactive CLI**: Interactively select models and ask questions.
6. **Batch Cleanup**: Delete temporary email data stored locally.

---

## Installation

### Prerequisites

- Python 3.8+
- Gmail API enabled and a `credentials.json` file downloaded for your Google Cloud project ([guide](https://developers.google.com/gmail/api/quickstart/python)).
- A valid Gemini API Key for Generative AI.

### Install Required Packages

Run the following command to install the required Python packages:

```bash
pip install -r requirements.txt
```

#### Example of `requirements.txt`
```plaintext
Flask
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
google-generativeai
```

---

## Setup

### 1. Configure Gmail API Credentials
Ensure you have a `credentials.json` file from your Google Cloud project. Place it in the root directory of this project.

### 2. Authentication
To generate a `token.json` file for authenticating with Gmail:
```bash
python generate_token.py
```
Follow the on-screen instructions to authorize the app.

---

## Running the Application

### 1. Start the Flask Server

Run the following command to start the Flask API server:
```bash
python gemini_email_agent_with_flask.py
```
The server will start at `http://localhost:5000`.

### 2. Using the Endpoints

#### List Models
Get a list of available Gemini models:
```bash
curl -X GET http://localhost:5000/models
```

#### Ask a Question
Send a query to a Gemini model:
```bash
curl -X POST http://localhost:5000/ask \
-H "Content-Type: application/json" \
-d '{
  "model_id": "gemini-1.5-flash-latest",
  "query": "What is the latest email about?"
}'
```

#### Cleanup Temporary Folder
Clear the locally stored email data:
```bash
curl -X POST http://localhost:5000/cleanup
```

---

## CLI Usage

### Download Emails
To download emails interactively or via CLI:
```bash
python gmail_agent.py --max 10 --showdownloadlog true
```

- `--max`: Limit the number of emails to download (default: no limit).
- `--showdownloadlog`: Show logs of downloaded emails (`true` or `false`).

### Start Server
To start the HTTP server for downloading emails:
```bash
python gmail_agent.py --server 5001
```

---

## Project Structure

```plaintext
.
├── gemini_email_agent_with_flask.py  # Flask API for Gemini Email Agent
├── gmail_agent.py                    # Main Gmail interaction and email download script
├── generate_token.py                 # Script to generate Gmail API token
├── email_loader.py                   # Utility for loading emails from temp folder
├── gemini_agent.py                   # Handles Gemini model selection and Q&A
├── credentials.json                  # Gmail API credentials (not included in repo)
├── token.json                        # Gmail API token (generated after auth)
├── temp/                             # Folder for storing downloaded emails
├── requirements.txt                  # Required Python packages
└── README.md                         # Project documentation
```

---

## Environment Variables

Set the following environment variable for authentication:
- **`GEMINI_API_KEY`**: Your Gemini API key for Generative AI.

Example:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

---

## Example Workflow

### 1. Authenticate and Download Emails
Run the following to authenticate and download emails:
```bash
python gmail_agent.py --max 5 --showdownloadlog true
```

### 2. Analyze Emails
Start the Flask API:
```bash
python gemini_email_agent_with_flask.py
```
Then, send a query to analyze your emails using a Gemini model:
```bash
curl -X POST http://localhost:5000/ask \
-H "Content-Type: application/json" \
-d '{
  "model_id": "gemini-1.5-flash-latest",
  "query": "Summarize my recent emails."
}'
```

---

## Contributing

Feel free to submit issues, pull requests, or suggestions for improvements.

---

## License

This project is licensed under the MIT License.

---

## Troubleshooting

- **Error: Invalid Credentials**  
  Regenerate the `token.json` file using:
  ```bash
  python generate_token.py
  ```

- **Gmail API Quota Limit**  
  Check your Gmail API quota in the Google Cloud Console.

- **Gemini API Errors**  
  Ensure your `GEMINI_API_KEY` is correctly set and has sufficient quota.
