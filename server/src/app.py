from flask import Flask, render_template, make_response,redirect, request,session,flash
import os
import functools
import datetime
# Import Firebase REST API library
import firebase
'''Import Modular page'''
from fireAuth import AuthHandler

'''import personalities list '''
from personalityList import PERSONALITYLIST,CATEGORYLIST,SOCIALBUTTERFLY,FOODIE,ARTISTIC,SCHOLAR,NEATNESS,COZYNESS,HOBBY


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
storage = firebaseApp.storage()

'''Define User Class'''
def calculateAge(userBday) :
  userBdayYear, userBdayMonth, userBdayDay = userBday.split('-')
  now = datetime.datetime.now()
  nowYear, nowMonth, nowDay = now.year,now.month,now.day
  dayDiff = int(nowDay) - int(userBdayDay)
  monthDiff = int(nowMonth) - int(userBdayMonth)
  if dayDiff < 0:
      monthDiff -= 1
  yearDiff = int(nowYear) - int(userBdayYear)
  if monthDiff < 0:
      yearDiff -= 1
  return yearDiff

def findCommon(userPersonality, SCORE_OR_ANOTHERUSER_LIST,PERSONALITYLIST=PERSONALITYLIST):
    # This function find what item are common in both 2 list ans return a list of common items
    LIST = list(SCORE_OR_ANOTHERUSER_LIST)
    common = []
    i,j = 0,0
    while i < len(userPersonality) and j < len(LIST):
        if userPersonality[i] == LIST[j]:
            common.append(userPersonality[i])
            i += 1
            j += 1
        elif PERSONALITYLIST.index(userPersonality[i]) < PERSONALITYLIST.index(LIST[j]):
            i += 1
        else:
            j += 1

    return common
        
def calulatePersonalityScore(userPersonality, SCORELIST,PERSONALITYLIST=PERSONALITYLIST):
    common = findCommon(userPersonality, SCORELIST)
    score = 0
    for item in common:
        if item in SCORELIST: 
            score += SCORELIST[item]

    return score

def calulateUserPersonalityScore(userPersonality,PERSONALITYLIST=PERSONALITYLIST,CATEGORYLIST=CATEGORYLIST):
    userPersonalityScore = {}
    for categoryName,scoreList in CATEGORYLIST.items(): 
        score = calulatePersonalityScore(userPersonality,scoreList)
        if score > 5:
            score = 5
        userPersonalityScore[categoryName] = score
    return userPersonalityScore
class User:
    def __init__(self,userEmail):
        self.userEmail = userEmail
    def importSelfData(self):
        self.userData = fsdb.collection('User').document(self.userEmail).get()
        try:
             #check if user already have their profile image
             #If user have -> self.userImg = imageURL from firestore
            self.userImg = storage.child(f"userFile/{self.userEmail}.jpg").get_url()
        except:
            #if not -> self.userImg
            self.userImg =  "https://firebasestorage.googleapis.com/v0/b/use-dormee.appspot.com/o/WebFile%2FmaleAvatra.svg?alt=media&token=5e136ced-47d7-4b0d-8257-c850bfe8dc41"
        try:
            #check if user already have interestedMate on firestore
            #If user have -> self.interestedMate = data from firestore
            self.interestedMate = self.userData['interestedMate']
        except:
            #if not -> self.interestedMate is created
            self.interestedMate = []
        try:
            #check if user already have ignoredMate on firestore
            #If user have -> self.ignoredMate = data from firestore
            self.ignoredMate = self.userData['ignoredMate']
        except:
            #if not -> self.ignoredMate is created
            self.ignoredMate = []
        #calculate user age from bDay relative to datetime.now
        self.userData['userAge'] = calculateAge(self.userData['bDay'])
    def addInterestedMate(self,mateEmail):
        #IMPORTANT : make sure to importSelfData(self) before running this method
        #this method updates self.interestedMate and update it on firestore
        self.interestedMate.append(mateEmail)
        data = {
            'interestedMate' : self.interestedMate
        }
        fsdb.collection('User').document(self.userEmail).update(data)
    def addIgnoredMate(self,mateEmail):
        #IMPORTANT : make sure to importSelfData(self) before running this method
        #this method updates self.ignoredMate and update it on firestore
        self.ignoredMate.append(mateEmail)
        data = {
            'ignoredMate' : self.ignoredMate
        }
        fsdb.collection('User').document(self.userEmail).update(data)
    def __str__(self): # return class object
        return f"User : {self.userEmail}"


class Recommender:
    def __init__(self):
        self.rankedMateByMatchPercent = []
        currentUser = User(session['user']['email'])
        currentUser.importSelfData()
        # Import possible mate who have at least one same interested dorm as currentUser
        mateDatabase = fsdb.collection('User').where('interestedDorm', 'array_contains_any',currentUser.userData['interestedDorm']).get()

        # Filter out currentUser,already interested,alredy ignored
        fliter = [currentUser.userEmail] + currentUser.interestedMate + currentUser.ignoredMate
        print(fliter)
        for mateDict in mateDatabase:
            # get dictionary of each possible mate
            for mateEmail in mateDict.keys():
                if not (mateEmail in fliter):
                    print('test',mateEmail)
                    mateEmail = User(mateEmail)
                    mateEmail.importSelfData()
                    
                    try:
                        #calculate matched %
                        commonList = findCommon(currentUser.userData['userPersonality'], mateEmail.userData['userPersonality'])
                        matchPercent = round((len(commonList) / len(currentUser.userData['userPersonality']))*100, 2)
                        self.rankedMateByMatchPercent.append((mateEmail.userEmail,matchPercent))
                    except:
                        #Mate's userPersonality not found
                        self.rankedMateByMatchPercent.append((mateEmail.userEmail,0))

        #sort rankedMateByMatchPercent
        self.rankedMateByMatchPercent.sort(key = lambda x: x[1] ,reverse=True)
    

    def giveRecommendedMate(self):
        recommendMate = self.rankedMateByMatchPercent[0]
        nextRecommendMate = self.rankedMateByMatchPercent[1]
        self.rankedMateByMatchPercent.pop(0)
        print(self.rankedMateByMatchPercent)
        return recommendMate,nextRecommendMate

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
        data = {
            'displayName' : request.form.get("displayName") ,
            'gender' : request.form.get("gender"),
            'bDay' : request.form.get("bDay") ,
            'religion' : request.form.get("religion") ,
            'contactNote' : request.form.get("contactNote") ,
            'healthNote' : request.form.get("healthNote"), 
            }
        userImg = request.files.get("userImg")
        user = session['user'] 
        fsdb.collection('User').document(user['email']).update(data)
        storage.child(f"userFile/{user['email']}.jpg").put(userImg)
    
        if data['displayName'] != None:
            return redirect('/form2')
    return runWithCacheControl(template)

@app.route('/form2',methods = ["GET","POST"])
@login_required
def form2():
    template = render_template('form2.html')
    if request.method == "POST":
        # getting input in HTML form
        data = {
            'university' : request.form.get("university-select") ,
            'faculty' : request.form.get("faculty-select"),
            'major' : request.form.get("major") ,
            'acedemicYear' : request.form.get("year") 
            }
        user = session['user'] 
        fsdb.collection('User').document(user['email']).update(data)
        if data['university'] != None:
            return redirect('/form3')   
    
    return runWithCacheControl(template)

@app.route('/form3',methods = ["GET","POST"])
@login_required
def form3():
    #initialize
    isSleepWithLightOn = ''
    userNote = ''
    userPersonality = []
    if request.method == "POST":
        isSleepWithLightOn = request.form.get("isSleepWithLightOn")
        if isSleepWithLightOn =='true':
            isSleepWithLightOn = True
        else:
            isSleepWithLightOn = False
        userNote = request.form.get("userNote")
        if userNote == '':
            userNote = 'ผู้ใช้ท่านนี้ไม่ได้ระบุโน๊ต'
    userPersonality = request.form.getlist("personalityForm")
    userPersonalityScore = calulateUserPersonalityScore(userPersonality)
    data = {
        'sleepTimeMin' : request.form.get("sleepTimeMinForm"),
        'sleepTimeMax' : request.form.get("sleepTimeMaxForm"),
        'isSleepWithLightOn' : isSleepWithLightOn,
        'userNote' : userNote,
        'userPersonality' : userPersonality,
        'userPersonalityScore' : userPersonalityScore
    }
    user = session['user']
    fsdb.collection('User').document(user['email']).update(data)
    if data['userPersonality'] != []:
        return redirect('/dorm_advise')
    template = render_template('form3.html')
    return runWithCacheControl(template)

@app.route('/dorm_advise',methods = ["GET","POST"])
@login_required
def dorm_advise():
    #initialize
    interestedDorm = []
    if request.method == "POST":
        interestedDorm = request.form.getlist("interestedDorm")
        data = {
            'interestedDorm' : interestedDorm
        }
        user = session['user']
        fsdb.collection('User').document(user['email']).update(data)
        if data['interestedDorm'] != []:
            return redirect('/findmate')
    template = render_template('dorm_advise.html')
    return runWithCacheControl(template)



@app.route('/findmate',methods = ["GET","POST"])
@login_required
def findmate():
    currentUser = User(session['user']['email'])
    print(currentUser)
    currentUser.importSelfData()
    x = Recommender()
    
    recommendedMateTuple,nextRecommendMateTuple = x.giveRecommendedMate()
    recommendedMate = User(recommendedMateTuple[0])
    recommendedMate.importSelfData()
    nextRecommendMate = User(nextRecommendMateTuple[0])
    nextRecommendMate.importSelfData()
    recommendedMateMatchPercent = recommendedMateTuple[1]
    nextRecommendMateMatchPercent = nextRecommendMateTuple[1]
    if request.method == "POST":
        mateStatus = request.form.get("mateStatus")
        if mateStatus == 'Interseted':
            currentUser.addInterestedMate(recommendedMate.userEmail)
        elif mateStatus == 'Ignored':
            currentUser.addIgnoredMate(recommendedMate.userEmail)
    
    return render_template('findmate.html', mate1=recommendedMate, mate2=nextRecommendMate, mate1MatchPercent=recommendedMateMatchPercent ,mate2MatchPercent=nextRecommendMateMatchPercent) 

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