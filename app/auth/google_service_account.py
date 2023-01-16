"""
Basic authentication using a service account

"""
import datetime
import requests

METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
SERVICE_ACCOUNT = 'default'

class Auth:
    def __init__(self, service_account=None):
        if service_account is None:
            service_account = SERVICE_ACCOUNT

        self.metadata_url = f"{METADATA_URL}/instance/service-accounts/{service_account}/token"

        self.cur_token = None
        self.token_expire = datetime.datetime.now()

    @property
    def access_token(self):
        curtime = datetime.datetime.now()
        if curtime >= self.token_expire:
            response = requests.get(self.metadata_url, headers=METADATA_HEADERS)
            response.raise_for_status()

            response = response.json()
            self.token_expire = curtime + datetime.timedelta(seconds=response['expires_in'])
            self.cur_token = response['access_token']
        return self.cur_token

    def authorize(self, headers):
        headers["Authorization"] = f"Bearer {self.access_token}"
        return headers