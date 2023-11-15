from flask import Flask, render_template, make_response,redirect,Blueprint,request,session
# Import Firebase REST API library
import firebase

import os
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

AuthHandler = Blueprint('AuthHandler', __name__,template_folder='templates')

firebaseConfig = {
  'apiKey': "AIzaSyCg_HRI6tZ-MGIDnWtOJ7KmjKtS9lkucKI",
  'authDomain': "use-dormee.firebaseapp.com",
  'projectId': "use-dormee",
  'storageBucket': "use-dormee.appspot.com",
  'messagingSenderId': "257935959517",
  'appId': "1:257935959517:web:164dfec3b77058e4674234",
  'measurementId': "G-X69RF0FDE1",
  'databaseURL': ""
};

# Instantiates a Firebase app
firebaseApp = firebase.initialize_app(firebaseConfig)



# Reference to auth service with provider secret from env variable
client_secret_config = {
   "client_id": os.environ.get("client_id"),
   "client_secret": os.environ.get("client_secret"),
   "redirect_uris": [os.environ.get("redirect_uris")]
}
#init FireAuth and Firestore
auth = firebaseApp.auth(client_secret=client_secret_config)
fsdb = firebaseApp.firestore()

@AuthHandler.route('/login')
def loginGoogle():
    return redirect(auth.create_authentication_uri('google.com'))

@AuthHandler.route('/__/auth/handler')
def googleCallback():
   user = auth.sign_in_with_oauth_credential(request.url)
   session['user'] = user
   session['userEmail'] = user['email']
   try:
      fsdb.collection('User').document(user['email']).get(token=user['idToken'])
   except:
      data = {
      "userEmail": user['email']
      }
      fsdb.collection('User').document(user['email']).set(data,token=user['idToken'])
   return redirect('/form')
      
@AuthHandler.route('/logout')
def logout():
    session.clear()
    return redirect('/') 
