from flask import Flask, render_template, make_response,redirect, request,session,flash
import os
import functools
# Import Firebase REST API library
import firebase
'''Import Modular page'''
from fireAuth import AuthHandler


app = Flask(__name__, static_folder="../../static")
app.secret_key = os.environ.get("app.secret_key")
app.register_blueprint(AuthHandler)


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
fsdb = firebaseApp.firestore()
'''Define Dorm and User Class'''
 


def runWithCacheControl(template):
    # Flask’s make_response make it easy to attach headers.
    response = make_response(template)
    #s-maxage property tells Firebase Hosting to keep the content in the cache for 10 minutes. During this 10 minute period Firebase Hosting will skip running your server code in Cloud Run and serve the cache content directly.
    response.headers['Cache-Control'] = 'public, max-age=300, s-maxage=600'
    return response

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        try:
            session['user']
        except KeyError:
            print('You must login to access this')
            return redirect('/accessDenied')

        return view(**kwargs)

    return wrapped_view


@app.route('/')
def index():
    # This is first page
    template = render_template('index.html')
    return runWithCacheControl(template)

# Denied access of those who don't have authentication
@app.route('/accessDenied')
def accessDenied():
    template = render_template('accessDenied.html')
    return runWithCacheControl(template)

# 4 step form for first-time user
@app.route('/form',methods = ["GET","POST"])
@login_required
def form():
    template = render_template('form.html')
    if request.method == "POST":
        # getting input in HTML form
        return redirect('/')
    data = {
        #TODO upload image is not working!!
        'userImg' : request.args.get("userImg"),
        'displayName' : request.args.get("displayName") ,
        'bDay' : request.args.get("bDay") ,
        'religion' : request.args.get("religion") ,
        'contactNote' : request.args.get("contactNote") ,
        'healthNote' : request.args.get("healthNote"), 
        }
    user = session['user'] 
    print(data)
    fsdb.collection('User').document(user['email']).update(data,token=user['idToken'])
    return runWithCacheControl(template)

@app.route('/form2',methods = ["GET","POST"])
@login_required
def form2():
    university = 'Waiting respond'
    if request.method == "POST":  
        university = request.form.get("university")
        
    template = render_template('form2.html',university = university)
    return runWithCacheControl(template)

@app.route('/form3')
@login_required
def form3():
    template = render_template('form3.html')
    return runWithCacheControl(template)

@app.route('/dorm_advise')
@login_required
def dorm_advise():
    template = render_template('dorm_advise.html')
    return runWithCacheControl(template)

@app.route('/findmate')
@login_required
def findmate():
    template = render_template('findmate.html')
    return runWithCacheControl(template)

@app.route('/matched')
@login_required
def matched():
    template = render_template('matched.html')
    return runWithCacheControl(template)

@app.route('/profile')
@login_required
def profile():
    template = render_template('profile.html')
    return runWithCacheControl(template)



if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))


'''dormitory = {
    'samyan' : {
                'Wish@samyan':[{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d15503.092044594936!2d100.5265177!3d13.732188!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e298d5a96b5d1f%3A0x33e9478f3a6f1ddf!2sWish%40SamYan!5e0!3m2!1sen!2sth!4v1698722114775!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                               {'linkImg':'https://project.zmyhome-image.sg-sin1.upcloudobjects.com/V13916/09-28-2022-05-50-2069126647.jpg'},
                               {'PriceMax':15000},
                               {'PriceMin':15000},
                               {'Rate':4.9},
                               {'interested':0}],
                'U center': [{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3875.725774228931!2d100.52440147469858!3d13.735045297681992!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e2992a8405a121%3A0x2d6d1fe416290ab8!2sU%20Center%201!5e0!3m2!1sen!2sth!4v1698722712298!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                             {'linkImg':'https://lh3.googleusercontent.com/p/AF1QipMFEoi4CUEPWOVL5LfuABEsGJeolh1y7X2dKNJo=s1360-w1360-h1020'},
                             {'PriceMax':9000},
                             {'PriceMin':1500},
                             {'Rate':0},
                             {'interested':0}],
                'ณ สุรวงศ์' : [{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3875.8145316362925!2d100.52572099999999!3d13.729675999999998!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e298d4721a7c03%3A0xcc3c4ee712aa0e6d!2sNa%20Surawong!5e0!3m2!1sen!2sth!4v1698722988599!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                               {'linkImg':'https://bcdn.renthub.in.th/listing_picture/201812/20181226/MZ67QL3k6SV4FhzRo5ih.jpg?class=doptimized'},
                               {'PriceMax':9000},
                               {'PriceMin':7000},
                               {'Rate':0},
                               {'interested':0}],
                'บ้านนเรศ' : [{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d15503.448608057348!2d100.5277799!3d13.7267944!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e29922734c2707%3A0xfdc8dc7667b0f37b!2z4Lia4LmJ4Liy4LiZ4LiZ4LmA4Lij4LioIDMzMw!5e0!3m2!1sen!2sth!4v1698723049768!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                              {'linkImg':'https://bcdn.renthub.in.th/listing_picture/201209/20120925/gNmGDAjiLrHjvtDYkU1U.jpg?class=doptimized'},
                              {'PriceMax':6500},
                              {'PriceMin':6500},
                              {'Rate':0},
                              {'interested':0}] 
            }
    ,'Bantatthong' : {
                'PUNICA':[{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d15502.20349636943!2d100.5220691!3d13.7456197!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e2996668e3c897%3A0x10c272609ef9ca57!2sPunica!5e0!3m2!1sen!2sth!4v1698723237971!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                          {'linkImg':'https://bcdn.renthub.in.th/listing_picture/202205/20220527/pbEjDwcYPtpga5JgwAwr.jpg?class=doptimized'},
                          {'PriceMax':0},
                          {'PriceMin':0},
                          {'Rate':0},
                          {'interested':0}],
                'สวัสดิ์อพาร์ทเม้นท์': [{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d15501.566434505648!2d100.5295512!3d13.7552419!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e29ecad3289f83%3A0x6c156819cd911d12!2z4Liq4Lin4Lix4Liq4LiU4Li04LmM4Lit4Lie4Liy4Lij4LmM4LiX4LmA4Lih4LiZ4LiX4LmM!5e0!3m2!1sen!2sth!4v1698723391738!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                                   {'linkImg':'https://wmcdn.renthub.in.th/listing_picture/202303/20230316/FQeFkGJ65wr8cRBFgdfq.jpg?desktop=true&class=doptimized'},
                                   {'PriceMax':0},
                                   {'PriceMin':0},
                                   {'Rate':0},
                                   {'interested':0}],
                'บ้านธรรมกิจ' : [{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d15501.437813129345!2d100.5267773!3d13.7571838!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e29978625f1901%3A0xd7e9aca09e87ddeb!2z4Lia4LmJ4Liy4LiZ4LiY4Lij4Lij4Lih4LiB4Li04LiIIChCYWFuIFRoYW0gTWEgS2l0KQ!5e0!3m2!1sen!2sth!4v1698723436627!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                                 {'linkImg':'https://bcdn.renthub.in.th/listing_picture/202302/20230206/tDZb6VygMfU36tEY7rb6.jpg?class=doptimized'},
                                 {'PriceMax':0},
                                 {'PriceMin':0},
                                 {'Rate':0},
                                 {'interested':0}] 
            }
    ,'Siam' : {
                'บ้านเฉลิมหล้า':[{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d15501.757753918304!2d100.5296912!3d13.7523529!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e29eca0a4dc2e7%3A0xfb1b0caa43d0fd4e!2z4Lia4Lij4Li04Lip4Lix4LiXIOC4muC5ieC4suC4meC5gOC4ieC4peC4tOC4oeC4q-C4peC5ieC4siDguIjguLPguIHguLHguJQ!5e0!3m2!1sen!2sth!4v1698745097210!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                                 {'linkImg':'https://bcdn.renthub.in.th/listing_picture/201210/20121010/kisGsghiRmAZC8gZ69zh.jpg?class=doptimized'},
                                 {'PriceMax':8000},
                                 {'PriceMin':5000},
                                 {'Rate':0},
                                 {'interested':0}],
                'แอท ราชเทวี': [{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d3875.505498327823!2d100.5327202!3d13.7483618!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e29fa62d8e9d4d%3A0x3cc20187110c16a!2z4LmB4Lit4LiXIOC4o-C4suC4iuC5gOC4l-C4p-C4tSBBVF9SYXRjaGF0aGV3aQ!5e0!3m2!1sen!2sth!4v1698745196685!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                                {'linkImg':'https://lh3.googleusercontent.com/p/AF1QipNfv4YEEVeLCfdjqhEB2KQO5-lnFic5QQrzHjgO=s1360-w1360-h1020'},
                                {'PriceMax':20900},
                                {'PriceMin':7900},
                                {'Rate':0},
                                {'interested':0}],
                'บ้านสุโขทัย' : [{'linkMap':'<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3875.4809558741886!2d100.5328333!3d13.7498447!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x30e29ecc9ce13b41%3A0x4cb78878831f2755!2sBan%20Sukhothai!5e0!3m2!1sen!2sth!4v1698745252171!5m2!1sen!2sth" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'},
                                {'linkImg':'https://lh3.googleusercontent.com/p/AF1QipN3ye89blzyKlc5CI7gR9cYgxYZCGn8_vhGvtez=s1360-w1360-h1020'},
                                {'PriceMax':7000},
                                {'PriceMin':5000},
                                {'Rate':0},
                                {'interested':0}]
            }
}'''