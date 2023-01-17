import flask
from flask import Flask, render_template
#import google.oauth2.credentials
#from google.auth import compute_engine
#import google.auth.transport.requests

from google.oauth2 import service_account

import requests
import os

_PROXY_PATH=None
FHIR_URL=os.getenv('TARGET_SERVICE_URL')
FHIR_VERSION = "4.0.1"

app = Flask(__name__)
_auth = None


def get_proxy_path(flask_request):
    """We'll use this for substituting url info passed to and from the FHIR """
    """server to allow clients to correctly interact with the server"""

    global _PROXY_PATH

    if _PROXY_PATH is None:
        base_url =  flask_request.base_url
        _PROXY_PATH=base_url[0:base_url.index("/", 10)]
    return _PROXY_PATH

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

@app.route('/fhir/<path:path>', methods=['GET'])
def reversible(path):
    global FHIR_URL
    if flask.request.method=='GET':
        auth = get_auth()

        major_version = FHIR_VERSION.split(".")[0]
        headers = {
            "Content-Type": f"application/fhir+json; fhirVersion={major_version}.0"
        }
        auth.authorize(headers)

        proxy_path = get_proxy_path(flask.request)
        original_url = flask.request.base_url
        backend_path = path.replace(proxy_path, FHIR_URL)
        url = f"{FHIR_URL}/{backend_path}"
        print(f"""Incoming url: {original_url}
target_url: {url}
proxy_path: {proxy_path}""")


        resp = requests.get(url, headers=headers)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        #print(f"The response content is: \n{resp.content}")
        response = flask.Response(resp.content.replace(bytes(FHIR_URL, 'utf8'), bytes(proxy_path, 'utf8')), resp.status_code, headers)

        return response

    else:
        return "GET is the only verb permitted with this service."

def get_auth():
    global _auth 

    if _auth is None:
        # Eventually, we may want to work a way to determine auth methods via the
        # yaml configuration
        from auth.google_service_account import Auth
        _auth = Auth()
    return _auth

if __name__ == "__main__":
    app.run(debug=True)