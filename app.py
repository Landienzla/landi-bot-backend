from flask import Flask, request
from flask.globals import request
from flask.helpers import make_response
from flask_pymongo import PyMongo
from flask_cors import CORS
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
import time
import itertools


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://landienzla:5513@cluster0.irgw0.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
CORS(app)
mongo = PyMongo(app)
db = mongo.db
col = db.instagramBot
# browser_options = Options()
# browser_options.add_argument("--headless")
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--disable-blink-features=AutomationControlled')
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--allow-running-insecure-content')
# browser = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
browser = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
@app.route('/')
def home_page():
    return "<h1>Hello From Flask</h1>"


@app.route('/login', methods=["POST"])
def login():
    global serviceStatus
    global username
    serviceStatus = "BUSY"
    requestData = json.loads(request.data)
    username = requestData["username"]
    password = requestData["password"]
    browser.get("https://www.instagram.com")
    time.sleep(3)
    username_area = browser.find_element_by_xpath(
        '//*[@id="loginForm"]/div/div[1]/div/label/input')
    username_area.click()
    time.sleep(1)
    username_area.send_keys(username)
    password_area = browser.find_element_by_xpath(
        '//*[@id="loginForm"]/div/div[2]/div/label/input')
    password_area.click()
    time.sleep(1)
    password_area.send_keys(password)
    browser.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]').click()
    return "Logged in as{}".format(username), 200
@app.route('/logout/<user>')
def logout(user):
    global serviceStatus
    global username
    browser.get(f'https://www.instagram.com/{user}')
    time.sleep(5)
    browser.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[6]/span/img').click()
    time.sleep(5)
    browser.find_element_by_xpath("//*[text()='Çıkış Yap']").click()
    username = "admin"
    serviceStatus = "IDLE"
    return "loggedOut", 200
@app.route('/<user>/followings')
def followings(user):
    userData = col.find_one({'username':user})
    # datas = []
    # for data in userData:
    #     print(data)
    #     datas.append(data)
    # print(datas)
    # for i in userData:
    #     print(i)
    res = make_response(json.dumps(userData, default=str))
    res.mimetype = 'application/json'
    # return  json.loads(json_util.dumps(userData.followers)),200
    return res,200
@app.route('/users')
def userList():
    users = col.find()
    usersData = []
    for i in users:
        usersData.append(i)
    res = make_response(json.dumps(usersData,default=str))
    res.mimetype = 'application/json'
    return res,200

@app.route('/<user>/updateList',methods=['POST'])
def updateList(user):
    requestData = json.loads(request.data)
    col.update_one({'username':user},{"$set": {'checkboxes': requestData}})
    return 'kk'

@app.route('/<user>/giveaway',methods=["POST"])
def commenter(user):
    userInfo = col.find_one({'username':user})
    # print(userInfo)
    userlist = []
    requestData = json.loads(request.data)
    for i in userInfo['checkboxes']:
        if userInfo['checkboxes'][i] == True:
            # print(userInfo['followerNicks'][int(i)])
            nick = ' '.__add__(userInfo['followerNicks'][int(i)])
            userlist.append(nick)
    # print(userlist)
    # print(len(userlist))
    browser.get(requestData['giveawayURL'])
    combineduserlist = list(itertools.combinations(userlist,int(requestData['tagCount'])))
    for i in range(len(combineduserlist)):  
        try:
            browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[3]').click()
            commentarea = browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[3]/div/form/textarea')
            commentarea.send_keys(combineduserlist[i])
            time.sleep(10)
            browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[3]/div/form/button[2]').click()
            time.sleep(60)
            
        except:
            print("ERROR")
            print("I was commenting" + combineduserlist[i])
            return 'sıçtık',400
    return "Anne bittii",200
if __name__ == "__main__":
    app.run()
