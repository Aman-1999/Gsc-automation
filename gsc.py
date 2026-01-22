from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GSCClient:
    def __init__(self, creds_data):
        self.credentials = Credentials(
            token=creds_data.get('token'),
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data.get('token_uri'),
            client_id=creds_data.get('client_id'),
            client_secret=creds_data.get('client_secret'),
            scopes=creds_data.get('scopes')
        )
        self.service = build('searchconsole', 'v1', credentials=self.credentials)

    def list_sites(self):
        """Fetch list of verified sites."""
        site_list = self.service.sites().list().execute()
        return site_list.get('siteEntry', [])

    def query_search_analytics(self, site_url, payload):
        """
        Execute a search analytics query.
        Payload should mimic the GSC API structure:
        {
            "startDate": "2023-01-01",
            "endDate": "2023-01-31",
            "dimensions": ["query", "page"],
            "rowLimit": 10
        }
        """
        return self.service.searchanalytics().query(
            siteUrl=site_url, 
            body=payload
        ).execute()
