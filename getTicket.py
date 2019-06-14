#!/usr/bin/python
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def getPageSource(ori,dst,date):
    driver = webdriver.Chrome(executable_path=r'./chromedriver')
    web = "https://www.google.com/flights?hl=zh-TW#flt=" + ori +"." + dst + "." + date + ";c:TWD;e:1;sd:1;t:f;tt:o"
    # driver.get('https://www.google.com/flights?hl=zh-TW#flt=TPE.GUM.2019-06-25*GUM.TPE.2019-06-29;c:TWD;e:1;sd:1;t:f')
    driver.get(web)
    pageSource = driver.page_source
    driver.close()
    soup = BeautifulSoup(pageSource, "html.parser")
    # print (soup.prettify())
    return soup

def getData(soup,target,db):
    result = soup.find_all("div", class_ = "gws-flights-results__collapsed-itinerary gws-flights-results__itinerary")
    print ("Get...")
    for plan in result :
        data = {}
        try:
            flyTime,landTime = getTime(plan)
            data = {
                'target' : target["id"],
                'plane' : getPlane(plan),
                'flyTime' : flyTime,
                'landTime' : landTime,
                'durationTime' : getDuration(plan),
                'price' : getPrice(plan).strip(),
                'img' : getImg(plan),
                'ori' : target["ori"],
                'dst' : target["dst"],
                'date' : target["date"]
            }
            
            addDatabase(data,db)
        except IndexError as e:
            # print (e)
            continue
    print ("Done...")

def addDatabase(data,db):
    path = "searchResult/" + data['target'] + "/tickets"
    id = data['plane'] + ":" + data['flyTime']
    doc_ref = db.collection(path).document(id)
    doc_ref.set(data)

    targetPath = "searchResult"
    exist = db.collection(targetPath).document(data['target'])
    exist.set({
        'exist' : True
    })
    
def getPlane(plan):
    plane = plan.select("span.gws-flights__ellipsize span span")[0].text
    return plane
def getTime(plan):
    times = plan.select("div.gws-flights-results__times-row span span span")
    flyTime = times[0].text
    landTime = times[1].text
    return flyTime,landTime

def getDuration(plan):
    duration = plan.select("div.gws-flights-results__duration")[0].text
    return duration

def getPrice(plan):
    price = plan.select("div.gws-flights-results__price")[0].text
    return price
def getImg(plan):
    img = "http:" + plan.find('img')['src']
    return img

def initDatabase():
    cred = credentials.Certificate('./ticketing-47821-firebase-adminsdk-u4pv5-2c7dab6044.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

def searchQuery():
    path = "query"
    querys = db.collection(path).get()
    for query in querys:
        print (query.id)
        date = query.get("date")
        ori = query.get("ori")
        dst = query.get("dst")
        target = {
            "id" : ori + dst + date,
            "ori" : ori,
            "dst" : dst,
            "date" : date
        } 
        soup = getPageSource(ori,dst,date)
        getData(soup,target,db)

def checkSub():
    path = "user"
    users = db.collection(path).get()
    for user in users:
        subPath = path + "/" + user.id + "/subscribe"
        subs = db.collection(subPath).get()
        for sub in subs:
            dataPath = "searchResult/" + sub.get("target") + "/tickets/" + sub.get("plane") + ":" + sub.get("flyTime");
            oldPath = subPath + "/" + sub.id
            data = db.document(dataPath).get().to_dict()
            oldData = db.document(oldPath)
            oldData.update(data)
            print(oldData.id)
            # print(data)

def testCrawl():
    ori = "TPE"
    dst = "KUL"
    date = "2019-07-01"
    target = {
            "id" : ori + dst + date,
            "ori" : ori,
            "dst" : dst,
            "date" : date
    }
    soup = getPageSource(ori,dst,date)
    getData(soup,target,db)

if __name__ == '__main__':
    db = initDatabase()
    
    # testCrawl()

    searchQuery()
    checkSub()