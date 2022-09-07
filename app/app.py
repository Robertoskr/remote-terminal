from http import HTTPStatus
import os
from flask import Flask, request
from typing import Optional
import requests
from requests import Response
import subprocess

app = Flask(__name__)

BASE_URL = "http://127.0.0.1"

def make_request(path: str, json: dict) -> Response: 
    # workaround to make requests to localhost
    session = requests.Session()
    session.trust_env = False
    return session.get(url=BASE_URL + path, json=json)

@app.route("/")
def home() -> dict:
    """
    Base endpoint, 
    returns the result of running ls -l in another machine 
    """
    producer_port: Optional[int] = os.getenv("PRODUCER_PORT")
    if not producer_port: 
        return {"error": "no producer port specified"}, HTTPStatus.BAD_REQUEST
    
    command: str = "ls -l"

    response: Response = make_request("/get_command", json=dict(command=command))
    json_response: dict = response.json()

    # get the total files from json response 
    return {"total_files": len(json_response["result"].split(" ")) - 1}, HTTPStatus.OK

@app.route("/command/<string:command>")
def request_command(command: str) -> dict:
    response: Response = make_request(f"/get_command", json=dict(command=command))
    try: 
        response_json = response.json()
    except: 
        response_json = {}

    return {"response": response_json}

@app.route("/get_command")
def get_command() -> dict:
    payload: dict = request.json
    try: 
        raw_command: str = payload["command"]
    except KeyError: 
        return {"error": "required command"}

    command_result = subprocess.run(raw_command.split(" "), stdout=subprocess.PIPE, text=True)
    return {"result": command_result.stdout}, HTTPStatus.OK

    
    

if __name__ == "__main__": 
    app.run(debug=True, host="0.0.0.0", port=80)
    