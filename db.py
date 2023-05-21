#from web_server import mongo
from flask import g, current_app
from flask_pymongo import PyMongo
from datetime import datetime

from pymongo.mongo_client import MongoClient

"""
{
  "_id": ObjectId("60c5c2f2f15e4b3dd8f3793e"),
  "user": {
    "phone_number": "+1234567890",
    "subscribed": true
  },
  "conversation_array": ["Hello", "How can I help you?", "Tell me a joke", "Why did the chicken cross the road?", "I don't know, why did the chicken cross the road?", "To get to the other side!"],
  "prompts_sent": 3,
  "session_start": ISODate("2023-05-17T00:00:00Z"),
  "session_end": ISODate("2023-05-17T00:30:00Z")
}

"""
uri = os.getenv("MONGO_DB_URI")
client = MongoClient(uri)
mongo_db_database = client['mysticmac_whatsapp_chatbot']
chat_sessions = mongo_db_database['chat_sessions']

# def get_db():
#     db = getattr(g, "_database", None)
#     if db is None:
#         db = g._database = PyMongo(current_app).db
#     return db

# db = LocalProxy(get_db)

def user_exists(phone_number):
    try:
        session_count = chat_sessions.count_documents({'phone_number': phone_number})
        return session_count > 0
    except Exception as e:
        print("error occurred in user_exits in db.py")
        print(e)
        return e

def insert_one_into_collection(phone_number, subscribed:bool, conversation_array, prompts_sent, starttime, endtime):
    try:
        chat_sessions.insert_one(
        {
            "user": {
                "phone_number": phone_number,
                "subscribed": subscribed
            },
            "conversation_array": conversation_array,
            "prompts_sent": prompts_sent,
            "session_start": starttime,
            "session_end": endtime
        }
        )
    except Exception as e:
        print("error occurred in insert one into collections in db.py")
        print(e)
        return e

def update_conversation_array(phone_number, message):
    try:
        chat_sessions.update_one({'phone_number': phone_number}, {'$push': {'conversation_array': message}})
    except Exception as e:
        print("error occurred in update conversation array in db.py")
        print(e)
        return e

def update_prompt_number(phone_number):
    try:
        # Retrieve the current session document
        session = chat_sessions.find_one({'phone_number': phone_number})
        
        # If the session exists and 'prompts_sent' field is present
        if session and 'prompts_sent' in session:
            prompts_number = session['prompts_sent'] + 1
        else:
            # If the session does not exist or 'prompts_sent' field is not present, start with 1
            prompts_number = 1
        
        # Update the 'prompts_sent' field in the database
        chat_sessions.update_one({'phone_number': phone_number}, {'$set': {'prompts_sent': prompts_number}})
    except Exception as e:
        print("Error occurred in update prompt number in db.py")
        print(e)
        return e


def update_session_start(phone_number, start_time):
    try:
        chat_sessions.update_one({'phone_number': phone_number}, {'$set': {'session_start': start_time}})
    except Exception as e:
        print("error occurred in update_session_start array in db.py")
        print(e)
        return e

def update_session_end(phone_number, end_time):
    chat_sessions.update_one({'phone_number': phone_number}, {'$set': {'session_end': end_time}})
    #db.chat_sessions.createIndex({ "session_end": 1 }, { expireAfterSeconds: 600 })


def get_prompts_sent(phone_number):
    session = mongo_db_database.chat_sessions.find_one({'phone_number': phone_number}, {'prompts_sent': 1, 'phone_number': 0})
    if session is not None:
        return session['prompts_sent']
    else:
        return None

def get_conversation_array(phone_number):
    session = chat_sessions.find_one({'phone_number': phone_number}, {'conversation_array': 1, 'phone_number': 0})
    if session is not None:
        return session['conversation_array']
    else:
        return None

