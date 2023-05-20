# My poor coding practice is shown here:
# even in the exceptions or errors I am returning ("HTTPS 200 OK", 200) because of the repeated webhook events. I need to solve it still.

import hashlib
import hmac
import os
import io

import dotenv
import openai
import requests
import speech_recognition as sr
from flask import Flask, json, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydub import AudioSegment

dotenv.load_dotenv() # Load environment variables from a .env file

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per seconds"])

# Set OpenAI API key and organization ID
openai.organization= os.getenv("OPENAI_ORGANIZATION")
openai.api_key=os.getenv("OPENAI_API_KEY")
open_ai_conversation_array = []

#meta's token
meta_permanent_token = os.getenv("META_PERMANENT_TOKEN")

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

1. Well so right now I am getting tons of requests for the message status. I need to figure out a way so that the whatsapp knows that I got the webhook. --> Fixed
"""
def sending_reply(senders_phone_number_id, message_id, reciepient_number, message):
    url = f"https://graph.facebook.com/v16.0/{senders_phone_number_id}/messages"
    headers = {
            "Authorization": f"Bearer {meta_permanent_token}",
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
        else:
            resp = {
                'status_code' : response.status_code, 
                'response' : response.reason,
                'body' : response.json()
            }
            #print("resp from sending reply is: ")
            #print(resp)
            # return "HTTPS 200 OK", 200
            return resp
    except Exception as E:
        print(f"Unexpected error: {E}")
        # Handle the error, or return an appropriate response
        return ("HTTPS 200 OK", 200)


"""
writing a function to download the audio file in a audio message:

According to facebook's documents [https://developers.facebook.com/docs/whatsapp/cloud-api/reference/media/#retrieve-media-url]

Retrieve Media URL

To retrieve your media’s URL, send a GET request to /MEDIA_ID. Use the returned URL to download the media file. Note that clicking this URL (i.e. performing a generic GET) will not return the media; you must include an access token. See Download Media [].

Sample request:

curl -X GET 'https://graph.facebook.com/v16.0/<MEDIA_ID>/' \
-H 'Authorization: Bearer <ACCESS_TOKEN>'

A successful response includes an object with a media url. The URL is only valid for 5 minutes. To use this URL, see Download Media.

{
  "messaging_product": "whatsapp",
  "url": "<URL>",
  "mime_type": "<MIME_TYPE>",
  "sha256": "<HASH>",
  "file_size": "<FILE_SIZE>",
  "id": "<MEDIA_ID>"
}

Download Media

To download media, make a GET call to your media’s URL. All media URLs expire after 5 minutes —you need to retrieve the media URL again if it expires. If you directly click on the URL you get from a /MEDIA_ID GET call, you get an access error.

Example

Sample request:

curl  \
 'URL' \
 -H 'Authorization: Bearer ACCESS_TOKEN' > media_file

If successful, you will receive the binary data of media saved in media_file, response headers contain a content-type header to indicate the mime type of returned data. Check supported media types for more information.

If media fails to download, you will receive a 404 Not Found response code. In that case, we recommend you try to retrieve a new media URL and download it again. If doing so doesn't resolve the issue, please try to renew the ACCESS_TOKEN then retry downloading the media.
"""

def audio_message(phone_number_id, audio_media_id):
    url = f"https://graph.facebook.com/v16.0/{audio_media_id}/"
    sending_headers = {
            "Authorization": f"Bearer {meta_permanent_token}",
    }
    try:
        """
        the reponse is the of the following format:
        {
            "messaging_product": "whatsapp",
            "url": "<URL>",
            "mime_type": "<MIME_TYPE>",
            "sha256": "<HASH>",
            "file_size": "<FILE_SIZE>",
            "id": "<MEDIA_ID>"
        }

        I need to extract the url and make a GET request on that URL. 
        """
        response = requests.get(url, headers=sending_headers).json()
        print("\nresponse in audio_message function")
        print(response)

        """
        The response would have the binary data of audio/ogg format. to access the binary content, I need to return response.content here. 
        """
        download_url = response['url']
        response = requests.get(download_url, headers=sending_headers)

        return response.content
    
    except requests.RequestException as re:
        print("\na request exception occurred in audio_message function")
        print(re)
        return ("HTTPS 200 OK", 200)
    except Exception as e:
        print("\n an error occurred in audio_message function")
        print(e)
        return ("HTTPS 200 OK", 200)

def transcribe_audio(binary_data):
    print("\n in audio transcribe method\n")
    try:
        # Create a file-like object from the binary data
        ogg_file_like = io.BytesIO(binary_data)

        # Load audio (ogg)
        audio = AudioSegment.from_ogg(ogg_file_like)

        # Export to wav (file-like object)
        wav_file_like = io.BytesIO()
        audio.export(wav_file_like, format='wav')

        # "Rewind" the file-like object
        wav_file_like.seek(0)

        # Transcribe audio file
        r = sr.Recognizer()
        with sr.AudioFile(wav_file_like) as source:
            audio = r.record(source)  # read the entire audio file
            #Google Speech Recognition (Hindi) results
            transcription_text = r.recognize_google(audio,language='hi-IN')
        print(type(transcription_text))
        print(f"transcription_text: {transcription_text}")
        return transcription_text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return ("HTTPS 200 OK", 200)
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ("HTTPS 200 OK", 200)
    except Exception as e:
        print("Exception occurred in transcribe method: " + str(e))
        return ("HTTPS 200 OK", 200)  # convert the exception to a string before returning it


def open_ai_trial(prompt):
    try:
        history = open_ai_conversation_array
        messages = []
        messages.append({"role": "system", "content": "You are ChatGPT, an advanced AI assistant developed by OpenAI and specially adapted by Rishabh Tyagi. You are interacting with Rishabh's parents, who are not very familiar with navigating technology. Your goal is to provide patient, respectful, and clear assistance to them as they learn to navigate and use their phone and other technology. Remember, your responses should be easy to understand, avoiding technical jargon whenever possible. You're here to make technology less intimidating and more accessible for them."})

        messages.append({"role": "user", "content": prompt})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages)
        reply = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": reply})
        return reply, messages

    except openai.InvalidRequestError as e:
        print(f"Invalid request: {e}")
        print("Invalid request", 400)
        return ("HTTPS 200 OK", 200)

    except openai.AuthenticationError as e:
        print(f"Authentication error: {e}")
        print("Authentication error", 401)
        return ("HTTPS 200 OK", 200)

    except openai.RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        print("Rate limit exceeded", 429)
        return ("HTTPS 200 OK", 200)

    except openai.APIError as e:
        print(f"API error: {e}")
        print("API error", 500)
        return ("HTTPS 200 OK", 200)

    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Unexpected error", 500)
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
                                        message_from = message.get('from')
                                        message_id = message.get('id')

                                        if message['type'] == "text":
                                            message_body = message.get('text', {}).get('body')
                                            reply_to_send, messages_array = open_ai_trial(message_body)
                                            
                                            if reply_to_send == "HTTPS 200 OK":
                                                print("I think an error occurred in open_ai_trial method")
                                                return ("HTTPS 200 OK", 200)

                                        elif message['type'] == "audio":
                                            audio = message["audio"]
                                            audio_media_id = audio["id"]
                                            response = audio_message(phone_number_id, audio_media_id)
                                            transcribed_text = transcribe_audio(response)

                                            reply_to_send, messages_array = open_ai_trial(transcribed_text)
                                            if reply_to_send == "HTTPS 200 OK":
                                                print("I think an error occurred in open_ai_trial method")
                                                return ("HTTPS 200 OK", 200)


                                        response = sending_reply(phone_number_id, message_id, message_from, reply_to_send)
                                        if response['status_code'] == 200:
                                            open_ai_conversation_array.append(messages_array)
                                            return 'HTTPS 200 OK', 200
                                        else:
                                            print("error occurred in sending the reply of the POST handler")
                                            print(response)
                                            return 'HTTPS 200 OK', 200
                                        
                            if 'statuses' in value:
                                statuses = value.get('statuses')
                                if statuses is not None:
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