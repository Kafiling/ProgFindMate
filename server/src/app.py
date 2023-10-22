from flask import Flask, render_template, make_response
import os


app = Flask(__name__, static_folder="../../static")

def runWithCacheControl(template):
    # Flask’s make_response make it easy to attach headers.
    response = make_response(template)
    #s-maxage property tells Firebase Hosting to keep the content in the cache for 10 minutes. During this 10 minute period Firebase Hosting will skip running your server code in Cloud Run and serve the cache content directly.
    response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
    return response

@app.route('/')
def index():
    # This is first page
    template = render_template('index.html')
    return runWithCacheControl(template)

@app.route('/register')
def register():
    template = render_template('register.html')
    return runWithCacheControl(template)
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))


