npx tailwindcss -i ./static/style.css -o ./static/tailwindoutput.css --watch

cd server
gcloud builds submit --tag gcr.io/use-dormee/flask-fire
gcloud beta run deploy --image gcr.io/use-dormee/flask-fire

cd ..
firebase deploy