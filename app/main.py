import flask
from flask import Flask, render_template
#import google.oauth2.credentials
#from google.auth import compute_engine
#import google.auth.transport.requests

from google.oauth2 import service_account

import requests
import os



FHIR_VERSION = "4.0.1"

app = Flask(__name__)
_auth = None

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
def reversible(path):

    if flask.request.method=='GET':
        auth = get_auth()
        fhir_url=os.getenv('TARGET_SERVICE_URL')

        major_version = FHIR_VERSION.split(".")[0]
        headers = {
            "Content-Type": f"application/fhir+json; fhirVersion={major_version}.0"
        }
        auth.authorize(headers)

        url = f"{fhir_url}/{path}"
        print(url)


        resp = requests.get(url, headers=headers)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in     resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = flask.Response(resp.content, resp.status_code, headers)

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