# Config Directory

Place your Google Cloud Service Account JSON file here.

## Setup Instructions:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable Google Sheets API
4. Create Service Account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Give it a name (e.g., "skylark-drone-coordinator")
   - Skip optional steps
5. Create Key:
   - Click on created service account
   - Keys tab → Add Key → Create New Key → JSON
   - Download the JSON file
6. Rename downloaded file to `service_account.json`
7. Place it in this directory: `config/service_account.json`

## Important Security Notes:

- **Never commit `service_account.json` to Git** (it's in .gitignore)
- For Streamlit Cloud deployment, paste JSON content into Streamlit Secrets instead
- Keep credentials secure and rotate periodically

## File Structure:

```
config/
├── README.md (this file)
└── service_account.json (your credentials - gitignored)
```
