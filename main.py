from flask import Flask, request
from twilio.rest import Client
import openai
from flask import Flask, request
from twilio.rest import Client
import openai
import os
from openai import OpenAI
import pandas as pd 
import json
from dotenv import load_dotenv
import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer

load_dotenv()

api_key= os.getenv("openai_api_key") 
client_openai = OpenAI(api_key=api_key)
app = Flask(__name__)
account_sid = os.getenv("twiliio_account_side")
auth_token = os.getenv("twillio_auth_token")
client = Client(account_sid, auth_token)

# Load the model
model = joblib.load('Trained_model.pkl')
vectorizer = CountVectorizer(decode_error="replace")
vectorizer.fit_transform(pd.read_csv("clean_dataset.csv")['message'])  # Make sure to fit_transform your original dataset's messages


def is_emergency(message):
    # Preprocess and transform the message to fit the model
    transformed_message = vectorizer.transform([message])
    prediction = model.predict(transformed_message)
    return prediction[0] == 'emergency'

def send_emergency_sms(message_body):
    message = client.messages.create(
        to="+923365562881",                                              # My phone number
        from_="+xxxxxxx",                           #My twillio phone number 
        body="URGENT! - " + message_body
    )
    print("Emergency message sent, SID:", message.sid)


@app.route('/webhook', methods=['POST'])  
def webhook_handler_emergency():
    data = request.json
    print(f"Received webhook data: {data}")  

    if 'data' in data and isinstance(data['data'], dict):
        nested_data = data['data']
        message_body = nested_data.get('body', "")
        if message_body:
            print(f"Processing message: {message_body}")
            if is_emergency(message_body):
                send_emergency_sms(message_body)
            else:
                print("Not an emergency.")
        else:
            print("No message body found in data.")
    else:
        print("Received data is not in the expected format or no nested 'data' field.")

    return "Webhook processed", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)