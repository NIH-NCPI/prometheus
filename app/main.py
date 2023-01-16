import flask
from flask import Flask, render_template
#import google.oauth2.credentials
#from google.auth import compute_engine
#import google.auth.transport.requests

from google.oauth2 import service_account

import requests
import os


METADATA_URL = 'http://metadata.google.internal/computeMetadata/v1/'
METADATA_HEADERS = {'Metadata-Flavor': 'Google'}
SERVICE_ACCOUNT = 'default'

FHIR_VERSION = "4.0.1"

app = Flask(__name__)

def get_access_token():
    url = '{}instance/service-accounts/{}/token'.format(
        METADATA_URL, SERVICE_ACCOUNT)

    # Request an access token from the metadata server.
    r = requests.get(url, headers=METADATA_HEADERS)
    r.raise_for_status()

    # Extract the access token from the response.
    access_token = r.json()['access_token']
    return access_token


@app.route("/", methods=['GET'])
def root():
    return f"""<p>The FHIR path is: <strong>{os.getenv("TARGET_SERVICE_URL", "??")} </strong>

<p>This is the root path for the FHIR server which doesn't do much. You should provide a meaningful FHIR query. 

<p>You don't care for me
<p>I don't care about that
<p>Gotta new fool
<p>I like it like that
<p>
<p>I have only one burnin' desire
<p>Let me stand next to your FHIR

<p>- J. Hendrix"""

@app.route('/<path:path>', methods=['GET'])
def reversable(path):

    if flask.request.method=='GET':
        fhir_url=os.getenv('TARGET_SERVICE_URL')
        access_token = get_access_token()

        major_version = FHIR_VERSION.split(".")[0]
        headers = {
            'Authorization': 'Bearer {}'.format(access_token),
            "Content-Type": f"application/fhir+json; fhirVersion={major_version}.0"
        }

        url = f"{fhir_url}/{path}"
        print(url)
        resp = requests.get(url, headers=headers)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in     resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = flask.Response(resp.content, resp.status_code, headers)

        return response

    else:
        return "GET is the only verb permitted with this service."

if __name__ == "__main__":
    app.run(debug=True)