import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]

MONETARY_SCOPE = "https://www.googleapis.com/auth/yt-analytics-monetary.readonly"

def get_credentials(
    credentials_file: str = "client_secret.json",
    token_file: str = "token.json",
    include_monetary: bool = False
) -> Credentials:
    """
    Retrieves or refreshes OAuth 2.0 user credentials.
    """
    scopes = list(DEFAULT_SCOPES)
    if include_monetary:
        scopes.append(MONETARY_SCOPE)

    creds = None
    
    # Load stored token if present
    if os.path.exists(token_file):
        try:
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        except Exception:
            creds = None

    # Refresh or create new token if invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
                
        if not creds:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"Credentials file '{credentials_file}' not found.\n"
                    "Please download your OAuth 2.0 Client Secret JSON from Google Cloud Console "
                    "and place it in this directory or pass the --credentials path."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(port=0)
            
        # Save token for next run
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return creds


def get_api_services(
    credentials_file: str = "client_secret.json",
    token_file: str = "token.json",
    include_monetary: bool = False
):
    """
    Returns initialized service clients for Data API v3, Analytics API v2, and Reporting API v1.
    """
    creds = get_credentials(credentials_file, token_file, include_monetary)
    
    youtube_data = build("youtube", "v3", credentials=creds)
    youtube_analytics = build("youtubeAnalytics", "v2", credentials=creds)
    youtube_reporting = build("youtubereporting", "v1", credentials=creds)
    
    return youtube_data, youtube_analytics, youtube_reporting
