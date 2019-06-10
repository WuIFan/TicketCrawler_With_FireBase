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
    #web = "https://www.google.com/flights?hl=zh-TW#flt=" + ori +"." + dst + "." + go
    # driver.get('https://www.google.com/flights?hl=zh-TW#flt=TPE.GUM.2019-06-25*GUM.TPE.2019-06-29;c:TWD;e:1;sd:1;t:f')
    driver.get(web)
    pageSource = driver.page_source
    driver.close()
    soup = BeautifulSoup(pageSource, "html.parser")
    # print (soup.prettify())
    return soup

def getData(soup,target,db):
    result = soup.find_all("div", class_ = "gws-flights-results__collapsed-itinerary gws-flights-results__itinerary")
    i = 0
    for plan in result :
        data = {}
        try:
            flyTime,landTime = getTime(plan)
            data = {
                'target' : target,
                'plane' : getPlane(plan),
                'flyTime' : flyTime,
                'landTime' : landTime,
                'durationTime' : getDuration(plan),
                'price' : getPrice(plan).strip(),
                'img' : getImg(plan)
            }
            
            print(data)
            addDatabase(data,db)
            # data.append(i)
            # data[i].time = text[0]
            #print ("plane:",plane,"fly:",flyTime,"land:",landTime,"duration:",durationTime,"price:",price)
        except IndexError:
            continue

def addDatabase(data,db):
    path = "searchResult/" + data['target'] + "/tickets"
    doc_ref = db.collection(path)
    doc_ref.add(data)

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
    img = plan.find('img')['src']
    return img

def initDatabase():
    cred = credentials.Certificate('./ticketing-47821-firebase-adminsdk-u4pv5-2c7dab6044.json')
    # 初始化firebase，注意不能重複初始化
    firebase_admin.initialize_app(cred)
    # 初始化firestore
    db = firestore.client()
    return db

if __name__ == '__main__': 
    # res = requests.get('https://www.google.com/flights?hl=zh-TW#flt=TPE.GUM.2019-06-25*GUM.TPE.2019-06-29;c:TWD;e:1;sd:1;t:f')
    # print(res.text)
    db = initDatabase()
    ori = "TPE"
    dst = "KUL"
    date = "2019-07-10"
    target = ori + dst + date 
    soup = getPageSource(ori,dst,date)
    getData(soup,target,db)


    
    