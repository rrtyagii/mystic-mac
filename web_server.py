import hashlib
import hmac
import os
import openai

import dotenv
from flask import Flask, json, request

dotenv.load_dotenv()

app = Flask(__name__)

openai.organization= os.getenv("OPENAI_ORGANIZATION")
openai.api_key=os.getenv("OPENAI_API_KEY")

def webhook_verification(hub_mode, hub_verify_token, hub_challenge):
    try:
        verification_token = os.getenv("META_VERIFICATION_TOKEN")

        if hub_mode == 'subscribe':
            if hub_verify_token == verification_token:
                return hub_challenge, 200
            else:
                print("Failed to verify webhook. Verification token does not match!")
                return "Error, wrong validation token", 403
        else:
            print("Failed to verify webhook. hub.mode is not subscribe ")
            return "Error, wrong validation token", 403
    except Exception as e:
        print(f"Unexpected error in webhook_verification: {e}")
        return "Unexpected error in webhook_verification", 500


def payload_verification(body, signature):
    try:
        if not signature:
            return f"Could not find signature: {signature} in the headers.", 400
        else:
            elements = signature.split('=')
            signature_hash = elements[1]
            app_secret = os.getenv("META_APP_SECRET")

            key = bytes(app_secret, 'UTF-8')
            expected_hash = hmac.new(key, msg=body, digestmod=hashlib.sha256).hexdigest()

            if (signature_hash!= expected_hash):
               response = "expected hash " + expected_hash + " signature hash " + signature_hash
               return response, 400
            else:
                return "HTTPS 200 OK", 200
    except IndexError:
        print("Error: Signature could not be split into two elements.")
        return "Error: Signature could not be split into two elements.", 400
    except Exception as e:
        print(f"Unexpected error in payload_verification: {e}")
        return f"Unexpected error in payload_verification: {str(e)}", 500
    

def fetch_requirements(data):
    try:
        for entries in data['entry']:
            for change in entries['changes']:
                value = change['value']
                if value:
                    phone_number_id = value['metadata']['phone_number_id']

                    if 'messages' in value:
                        if(value['messages'] is not None):
                            for message in value['messages']:

                                if message['type'] == "text":
                                    message_from = message['from']
                                    message_body = message['text']['body']
                                    message_id = message['id']

        return ((phone_number_id, message_id, message_from),"HTTPS 200 OK", 200)

    except KeyError as e:
        print(f"KeyError: {e}")
        # Handle the error, or return an appropriate response
        return ("Error in fetching requirements", 500)

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle the error, or return an appropriate response
        return ("Unexpected error", 500)

def sending_reply(senders_phone_number_id, reciepient_number, message_id, message):
    pass

@app.route("/", methods=['POST', 'GET'])
def home():
    output = (f"URL: {request.url}") + (f"Method: {request.method}") + (f"Headers: {request.headers}") + (f"Args: {request.args}") + (f"Data: {request.data}") + (f"Form: {request.form}")

    if request.method == "POST":
        output=request.get_json()
        return output

    if request.method == "GET":
        response = output
        return response
     
    
@app.route('/payload', methods=['POST', 'GET'])
def payload_api():
    if request.method == "POST":
        data=request.get_data()
        signature = request.headers.get('X-Hub-Signature-256')
        validate_payload = payload_verification(data, signature)
        if validate_payload[1] == 200:
            result, response, status_code = fetch_requirements(request.json)
            print(result)
        return (response, status_code)

    if request.method == "GET":
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')

        print(f"hub.mode: {hub_mode}")
        print(f"hub.challenge: {hub_challenge}")
        print(f"hub.verify_token: {hub_verify_token}")

        validate_payload = webhook_verification(hub_mode, hub_verify_token, hub_challenge)
        return validate_payload

if __name__ == '__main__':
    app.run(debug=True)
