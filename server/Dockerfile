# 1 base image of the container. Your code will run on a version of Python 3.12
FROM python:3.12

# 2 Install the needed dependencies to run the server: Flask and gunicorn.
RUN pip install Flask gunicorn

# 3 Install production dependencies.
RUN pip install firebase-rest-api
RUN pip install python-dotenv
#RUN pip install Flask-Session
# 4
COPY src/ /app
COPY src/ /fireAuth
COPY src/ /.env
WORKDIR /app

# 5
ENV PORT 8080

# 6
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app