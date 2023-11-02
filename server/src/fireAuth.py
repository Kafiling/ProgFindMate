import pyrebase

firebaseConfig = {
  'apiKey': "AIzaSyCg_HRI6tZ-MGIDnWtOJ7KmjKtS9lkucKI",
  'authDomain': "use-dormee.firebaseapp.com",
  'projectId': "use-dormee",
  'storageBucket': "use-dormee.appspot.com",
  'messagingSenderId': "257935959517",
  'appId': "1:257935959517:web:164dfec3b77058e4674234",
  'measurementId': "G-X69RF0FDE1"
};

firebase = pyrebase.initialize_app(firebaseConfig)
# Get a reference to the auth service
auth = firebase.auth()
auth.GoogleAuthProvider 