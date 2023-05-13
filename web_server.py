import hmac, hashlib
from flask import Flask, request, json
import dotenv, os

dotenv.load_dotenv()

app = Flask(__name__)

def webhook_verification(hub_mode, hub_verify_token, hub_challenge):
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

def payload_verification(body, signature):
    if not signature:
        return f"Could not find signature: {signature} in the headers.", 400
    else:
        try:
            elements = signature.split('=')
            signature_hash = elements[1]
            app_secret = os.getenv("META_APP_SECRET")

            key = bytes(app_secret, 'UTF-8')
            expected_hash = hmac.new(key, msg=body, digestmod=hashlib.sha256).hexdigest()

            if (signature_hash!= expected_hash):
               response = "expected hash " + expected_hash + " signature hash " + signature_hash
               return response, 400
            else:
                return "OK HTTPS", 200
        except Exception as e:
            print(e)
            print(e.with_traceback)
            print()
            return str(e), 500


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
        print(signature)
        response = payload_verification(data, signature)
        print(response)
        return response

    if request.method == "GET":
        hub_mode = request.args.get('hub.mode')
        hub_challenge = request.args.get('hub.challenge')
        hub_verify_token = request.args.get('hub.verify_token')

        print(f"hub.mode: {hub_mode}")
        print(f"hub.challenge: {hub_challenge}")
        print(f"hub.verify_token: {hub_verify_token}")

        response = webhook_verification(hub_mode, hub_verify_token, hub_challenge)
        return response

if __name__ == '__main__':
    app.run(debug=True)
