import hashlib
import hmac
import os
import openai
import requests

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
    

# def fetch_requirements(data):
    resp = {
        'status_code': 500, 
        'response': "Error in fetching requirements",
        'phone_number_id': '', 
        'message_from' : '',
        'message_id':''
    }

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

                                    resp['status_code'] = 200
                                    resp['response'] = "HTTPS 200 OK" 
                                    resp['phone_number_id'] = phone_number_id
                                    resp['message_from'] = message_from
                                    resp['message_id'] = message_id

        return resp

    except KeyError as e:
        print(f"KeyError: {e}")
        # Handle the error, or return an appropriate response
        return resp

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle the error, or return an appropriate response
        return resp

def fetch_requirements(data):
    resp = {
        'status_code': 500, 
        'response': "Error in fetching requirements",
        'phone_number_id': '', 
        'message_from' : '',
        'message_id':''
    }

    resp_status = {
        'status_code': 500, 
        'response': "Error in fetching requirements",
        'status_id': '', 
        'status_value' : '',
        'status_timestamp':'',
        'recipient_id' : ''
    }
    
    try:
        for entries in data.get('entry', []):
            for change in entries.get('changes', []):
                value = change.get('value', {})
                if value:
                    metadata = value.get('metadata', {})
                    phone_number_id = metadata.get('phone_number_id')

                    # Check for 'messages'
                    messages = value.get('messages')
                    if messages is not None:
                        for message in messages:
                            if message.get('type') == "text":
                                message_from = message.get('from')
                                message_body = message.get('text', {}).get('body')
                                message_id = message.get('id')

                                resp['status_code'] = 200
                                resp['response'] = "HTTPS 200 OK" 
                                resp['phone_number_id'] = phone_number_id
                                resp['message_from'] = message_from
                                resp['message_id'] = message_id

                    # Check for 'statuses'
                    statuses = value.get('statuses')
                    if statuses is not None:
                        for status in statuses:
                            status_id = status.get('id')
                            status_value = status.get('status')
                            status_timestamp = status.get('timestamp')
                            recipient_id = status.get('recipient_id')

                            resp_status['status_code'] = 200
                            resp_status['response'] = "HTTPS 200 OK" 
                            resp_status['status_id'] = status_id
                            resp_status['status_value'] = status_value
                            resp_status['status_timestamp'] = status_timestamp
                            resp_status['recipient_id'] = recipient_id
                   
                    print("resp_status")
                    print(resp_status)

        return resp

        # Modify the return statement to include the new values

    except KeyError as e:
        print(f"KeyError: {e}")
        # Handle the error, or return an appropriate response
        return resp

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Handle the error, or return an appropriate response
        return ("Unexpected error", 500)


def sending_reply(senders_phone_number_id, message_id, reciepient_number, message):
    url = f"https://graph.facebook.com/v16.0/{senders_phone_number_id}/messages"
    permanent_token = os.getenv("META_PERMANENT_TOKEN")
    headers = {
            "Authorization": f"Bearer {permanent_token}",
            "Content-Type": "application/json"
        }
    data = {
        "messaging_product": "whatsapp",
        "context": {
            "message_id": message_id
        },
        "recipient_type": "individual",
        "to": reciepient_number,
        "type": "text",
        "text": { 
            "preview_url": False,
            "body": message
            }
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        resp = {
            'status' : 200, 
            'response' : 'HTTPS 200 OK',
            'body' : response.json
        }
        return resp
    except Exception as E:
        print(f"Unexpected error: {E}")
        # Handle the error, or return an appropriate response
        return (f"Unexpected error {str(E)}", 500)


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
            result = fetch_requirements(request.json)
            if result['status_code'] == 200:
                 result2 = sending_reply(result['phone_number_id'], result['message_id'], result['message_from'], "Trying to send reply with permanent token")
            print(f"result {str(result)}")
            print()
            print(f"result 2{str(result2)}")
            print()
        return ('HTTPS 200 OK', 200)

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
