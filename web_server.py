
import hashlib
import hmac
import os

import dotenv
import openai
import requests
from flask import Flask, json, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_pymongo import PyMongo

dotenv.load_dotenv() # Load environment variables from a .env file

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per seconds"])

# Set OpenAI API key and organization ID
openai.organization= os.getenv("OPENAI_ORGANIZATION")
openai.api_key=os.getenv("OPENAI_API_KEY")

# Verify the webhook from Facebook's servers
"""
returning HTTPS 200 ok even in except block because that's what facebook's API docs ssays. 

https://stackoverflow.com/questions/75882393/whatsapp-business-api-webhook-getting-triggered-automatically
"""
def webhook_verification(hub_mode, hub_verify_token, hub_challenge):
    try:
        verification_token = os.getenv("META_VERIFICATION_TOKEN")

# If the incoming request is a subscription confirmation
        if hub_mode == 'subscribe':
            # If the verification token matches the expected token
            if hub_verify_token == verification_token:
                # Return the challenge passed in the request
                return hub_challenge, 200
            else:
                print("Failed to verify webhook. Verification token does not match!")
                return "Error, wrong validation token", 403
        else:
            print("Failed to verify webhook. hub.mode is not subscribe ")
            return "Error, wrong validation token", 403
    except Exception as e:
        print(f"Unexpected error in webhook_verification: {e}")
        return ("HTTPS 200 OK", 200)


# Verify the payload signature to ensure it's from Facebook
def payload_verification(body, signature):
    try:
        if not signature:
            return f"Could not find signature: {signature} in the headers.", 400
        else:
            elements = signature.split('=')
            signature_hash = elements[1]
            app_secret = os.getenv("META_APP_SECRET")

            # Create a hash using the app secret and the incoming message
            key = bytes(app_secret, 'UTF-8')
            expected_hash = hmac.new(key, msg=body, digestmod=hashlib.sha256).hexdigest()
            
            # Compare the hash with the hash from the incoming message
            if (signature_hash!= expected_hash):
               response = "expected hash " + expected_hash + " signature hash " + signature_hash
               return response, 400
            else:
                return "HTTPS 200 OK", 200
    except IndexError:
        print("Error: Signature could not be split into two elements.")
        return ("HTTPS 200 OK", 200)
    except Exception as e:
        print(f"Unexpected error in payload_verification: {e}")
        return ("HTTPS 200 OK", 200)

"""
To do:

1. Well so right now I am getting tons of requests for the message status. I need to figure out a way so that the whatsapp knows that I got the webhook. 
"""
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
            },
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            resp = {
                'status_code' : response.status_code, 
                'response' : 'HTTPS 200 OK',
                'body' : response._content
            }
            #print("resp from sending reply is: ")
            #print(resp)
            # return "HTTPS 200 OK", 200
            return resp
    except Exception as E:
        print(f"Unexpected error: {E}")
        # Handle the error, or return an appropriate response
        return ("HTTPS 200 OK", 200)


def open_ai_trial(prompt):
    try:
        messages = []
        messages.append({"role": "system", "content": "You are a friendly, helpulful, loving, polite large language model called BetaGPT trained by Rishabh Tyagi, based on the GPT-4 architecture."})

        messages.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages)
        reply = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": reply})
        return reply, messages
    except Exception as E:
        print(f"Unexpected error: {E}")
        # Handle the error, or return an appropriate response
        return ("HTTPS 200 OK", 200)


@app.route("/", methods=['POST', 'GET'])
#@limiter.limit("5 per second")
def home():
    output = (f"URL: {request.url} \n") + (f"Method: {request.method} \n") + (f"Headers: {request.headers} \n") + (f"Args: {request.args} \n") + (f"Data: {request.data} \n") + (f"Form: {request.form} \n")

    if request.method == "POST":
        output=request.get_json()
        return output

    if request.method == "GET":
        response = output
        return response
     
    
@app.route('/payload', methods=['POST', 'GET'])
#@limiter.limit("1 per second") #maximum of 6 requests per minute or 1 request per 10 seconds. 
def payload_api():
    if request.method == "POST":
        data=request.get_data()
        signature = request.headers.get('X-Hub-Signature-256')
        validate_payload = payload_verification(data, signature)
        if validate_payload[1] == 200:
            data = request.json

            try:
                for entries in data['entry']:
                # Iterate through the changes in each entry
                    for change in entries['changes']:
                        value = change.get('value', {})
                        if value:
                            metadata = value['metadata']
                            phone_number_id = metadata.get('phone_number_id')
                            
                            #Check for 'messages' in the value
                            if 'messages' in value:
                                messages = value['messages']
                                if messages is not None:
                                    print("\nmessages:")
                                    print(messages)
                                    for message in messages:
                                        if message['type'] == "text":
                                            message_from = message.get('from')
                                            message_body = message.get('text', {}).get('body')
                                            message_id = message.get('id')
                                        elif message['type'] == "audio":
                                            
                                            pass

                                reply_to_send, messages_array = open_ai_trial(message_body)
                                response = sending_reply(phone_number_id, message_id, message_from, reply_to_send)

                                print("\nmessasges array")
                                print(messages_array)

                                if response['status_code'] == 200:
                                    #print(response['body'])
                                    return 'HTTPS 200 OK', 200
                            
                            if 'statuses' in value:
                                statuses = value.get('statuses')
                                if statuses is not None:
                                    # print("statuses: \n")
                                    # print(statuses)
                                    return "HTTPS 200 OK", 200
    
            except KeyError as e:
                print(f"KeyError: {e}")
                # Handle the error, or return an appropriate response
                return ("HTTPS 200 OK", 200)

            except Exception as e:
                print(f"Unexpected error: {e}")
                # Handle the error, or return an appropriate response
                return ("HTTPS 200 OK", 200)

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