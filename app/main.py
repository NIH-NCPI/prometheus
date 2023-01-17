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
        _PROXY_PATH=base_url[0:base_url.index("/", 10)] + "/fhir"
    return _PROXY_PATH

@app.route("/", methods=['GET'])
def root():
    return f"""<p>The FHIR path is: <strong>{os.getenv("TARGET_SERVICE_URL", "??")} </strong>

<p>This is the root path for the FHIR server which doesn't do much. You should provide a meaningful FHIR query. 
<p>Some example queries include: 
<p><a href=https://nih-ncpi.github.io/ncpi-fhir-ig/>NCPI FHIR IG</a>
<p><a href=fhir/CodeSystem>IG CodeSystems Loaded</a>
<p><a href=fhir/ValueSet>IG ValueSets Loaded</a>
<p><a href=fhir/StructureDefinition>IG Profiles Loaded</a>
<p><a href=fhir/ResearchStudy>Research Studies Loaded</a>

<p>
<hr>
<pre>

You don't care for me
I don't care about that
Gotta new fool
I like it like that

I have only one burnin' desire
Let me stand next to your FHIR

- J. Hendrix
</pre>"""

@app.route('/fhir/<path:resource>', methods=['GET'])
def reversible(resource):
    global FHIR_URL

    if flask.request.method=='GET':
        auth = get_auth()

        query = []
        # Build the full query using whatever args were provided
        for arg,val in flask.request.args.items():
            query.append(f"{arg}={val}")
        if len(query) > 0:
            query = "?" + "&".join(query)
        else:
            query = ""
        fhir_query = f"{resource}{query}"
        print(f"RESOURCE: {resource}\nFHIR QRY: {fhir_query}")

        major_version = FHIR_VERSION.split(".")[0]
        headers = {
            "Content-Type": f"application/fhir+json; fhirVersion={major_version}.0"
        }
        auth.authorize(headers)

        proxy_path = get_proxy_path(flask.request)
        original_url = flask.request.base_url
        backend_path = fhir_query.replace(proxy_path, FHIR_URL)
        url = f"{FHIR_URL}/{backend_path}"
        print(f"""FHIR_URL: {FHIR_URL}
Incoming url: {original_url}
target_url: {url}
proxy_path: {proxy_path}
backend_path: {backend_path}

final_url: {url}""")


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