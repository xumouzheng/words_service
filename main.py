#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource,request
import hashlib,json
import os
import MySQLdb
import time
import datetime

app = Flask(__name__)
api = Api(app)

tokenList={
    'user1':"xzcczxc"
}

def loadJson():
    with open('words.json','r', encoding='UTF-8') as json_file:
        result = json.loads(json_file.read())
        return result['list']

allWords=loadJson()

def toMysql(sql):
    db = MySQLdb.connect("192.168.2.35", "python", "python", "app", charset='utf8', port=3306)
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    db.commit()
    db.close()
    return results

# get user's passwordMd5
def passwordMd5(username):
    sql="SELECT password_md5 FROM users WHERE `name`='"+username+"' LIMIT 1"
    results = toMysql(sql)
    if len(results)==0:
        return "-1"
    password_md5 = results[0][0]
    return password_md5
                                    


# everyDay create each user's task
def createTodayTask():
    today=datetime.date.today()
    sql="SELECT id,every_day_number FROM users"
    alluserInfo=toMysql(sql)
    for row in alluserInfo:
        sql="SELECT end_index FROM history WHERE create_time < '"+str(today)+"' AND user_id="+str(row[0])+" ORDER BY create_time DESC LIMIT 1"
        result=toMysql(sql)
        start_index=str(int(result[0][0])+1)
        end_index=str(int(start_index)+int(row[1]))
        print(start_index,end_index)
        sql="INSERT INTO history (user_id,create_time,start_index,end_index) VALUES ("+str(row[0])+",'"+str(today)+"',"+start_index+","+end_index+")"
        print(toMysql(sql))


def getUserId(username):
    sql="SELECT id FROM users WHERE `name`='"+username+"' LIMIT 1"
    userId=toMysql(sql)
    return userId[0][0]


def getUserTask(username):
    lists={
        'data0':[],
        'data1':[],
        'data2':[],
        'data3':[],
        'data4':[],
        'data5':[],
    }
    userId=str(getUserId(username))
    today=datetime.date.today()
    day1=str(today-datetime.timedelta(days=1))
    day2=str(today-datetime.timedelta(days=2))
    day4=str(today-datetime.timedelta(days=4))
    day7=str(today-datetime.timedelta(days=7))
    day15=str(today-datetime.timedelta(days=15))
    sql="SELECT start_index,end_index FROM history WHERE \
	        create_time = '"+str(today)+"' \
         OR create_time = '"+day1+"' \
         OR create_time = '"+day2+"' \
         OR create_time = '"+day4+"' \
         OR create_time = '"+day7+"' \
         OR create_time = '"+day15+"' AND user_id ="+userId+" ORDER BY create_time DESC"
    result=toMysql(sql)
    if(len(result)>0):
        index=0
        for row in result:
            print(index,row)
            for i in range (int(row[0]),int(row[1])):
                lists['data'+str(index)].append(allWords[i])
            index=index+1
        # print(lists)
        return lists
    else:
        return "error"

loginer=reqparse.RequestParser()
loginer.add_argument('username')
loginer.add_argument('password')

#create token
def create_token(username):
    token=hashlib.sha1(os.urandom(24)).hexdigest()
    save_token(username,token)
    return token

def save_token(username,token):
    tokenList[username]=token
    print(tokenList)

def check_token():
    authorization= request.headers.get('Authorization')
    if authorization=="ricky.test":    # 临时调试接口使用
        return "ricky"
    data=authorization.split(".")
    print(data,tokenList)
    if data[0] not in tokenList:
        return 0
    if tokenList[data[0]]==data[1]:
        return data[0]
    else :
        return 0


def test():
    lists={
        'data0':[],
        'data1':[],
        'data2':[],
        'data3':[],
        'data4':[],
        'data5':[],
    }
    for index in range (0,4):
        lists['data'+str(3)].append(allWords[index])
    print(lists)



def response(data,status):
    return {"data":data,"status":status}

# login
class Login(Resource):
    def post(self):
        args = loginer.parse_args()
        if args['password']==passwordMd5(args['username']):
            return response(create_token(args['username']),"ok")
        else: 
            return response("","error")

WordsList_args=reqparse.RequestParser()
WordsList_args.add_argument('start')
WordsList_args.add_argument('end')
class WordsList(Resource):
    # 获取所有单词列表
    def get(self):
        if check_token():
            return allWords
        else:
            return 'auth error'


    # 获取从范围是[n1,n2]的单词列表
    def post(self):
        args=WordsList_args.parse_args()
        lists=[]
        for index in range (int(args['start']),int(args['end'])):
            lists.append(allWords[index])
        return lists


# 获取当天任务（包括艾宾浩斯曲线要复习的）
class GetTasks(Resource):
    def get(self):
        username=check_token()
        print(username)
        if username:
            return response(getUserTask(username),"ok")
        else:
            return response("",'error')

# 每天定时程序调用，创建当天所有用户的任务数据
class CreateTask(Resource):
    def get(sef):
        createTodayTask()


##
## Actually setup the Api resource routing here
##
api.add_resource(Login, '/api/login')
api.add_resource(WordsList, '/api/wordslist')
api.add_resource(GetTasks, '/api/getTasks')
api.add_resource(CreateTask, '/createTask')


if __name__ == "__main__":
    # 将host设置为0.0.0.0，则外网用户也可以访问到这个服务
    app.run(host="0.0.0.0", port=8383, debug=True)