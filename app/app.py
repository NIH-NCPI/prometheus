from flask import Flask,request,redirect,Response
import requests
from os import getenv

import google
import google.oauth2.credentials
from google.auth import compute_engine
import google.auth.transport.requests

app = Flask(__name__)

@app.route("/")
def index():
    return f"""
    This is the base URL of prometheus and doesn't really do much. You should provide a valid FHIR query containing a resource type or operation name."""

@app.route('/<path:path>', methods=['GET'])
def reverseit(path):
    if request.method=='GET':
        resp = requests.get(f"{getenv('TARGET_URL', 'http://localhost:8000')}/{path}")
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in     resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
