from selenium import webdriver
from bs4 import BeautifulSoup
from pandas import DataFrame as df
import pandas
import requests
import re
import time
import os

url_rank = "https://www.bilibili.com/ranking"
url_login = "https://passport.bilibili.com/login"
path = "./"
data = df([])
rank = []
href = []
title = []
play = []
danmu_num = []
author = []
danmu = []
cid = []

#获得视频的chatid
def getCid(url):
    global browser
    browser.get(url)
    time.sleep(1)
    source = browser.page_source.encode('utf-8')
    soup = BeautifulSoup(source,'html.parser')
    tmp = ""
    pattern = re.compile(r"/[0-9]{9}/")#匹配cid
    items = soup.find_all("script")
    for item in items:
        tmp += str(item)
    chatid = pattern.search(tmp).group(0)
    return chatid[1:10]

#获得对应chatid的弹幕
def getDanmu(chatid):
    global browser
    date = time.strftime("%Y-%m-%d", time.localtime())
    danmu_url='https://api.bilibili.com/x/v2/dm/history?type=1&oid={0}&date={1}'.format(chatid,date)
    browser.get(danmu_url)
    source = browser.page_source.encode('utf-8')
    danmu = []
    soup = BeautifulSoup(source,'html.parser')
    items = soup.find_all('d')
    for item in items:
        danmu.append(item.text)
    return danmu

#打印进度条
def progress(t):
    print("\r%02d%%"%(t+1),end = '')

browser = webdriver.Chrome()

browser.get(url_login)
print("请登录您的账号")
os.system("pause")

browser.get(url_rank)
source = browser.page_source.encode("utf-8")

soup = BeautifulSoup(source,'html.parser')
items = soup.find_all(class_='rank-item')

t = 0

#获取排行榜信息
for item in items:
    #排名
    rank.append(item.get('data-rank'))
    infos = item.find_all(class_='info')
    for info in infos:
        #超链接和标题的class
        hrefs_titles = info.find_all(class_="title")
        for href_title in hrefs_titles:
            #超链接
            url_tmp = href_title.get('href')
            href.append(url_tmp)
            #获取视频cid
            cid_tmp = getCid(url_tmp)
            cid.append(cid_tmp)
            danmu.append(getDanmu(cid_tmp))
            #标题
            title.append(href_title.text)

            progress(t)
            t += 1

        #播放量，弹幕量，作者的class
        details = info.find_all(class_='detail')
        for detail in details:
            plays_danmunum_authors = detail.find_all(class_='data-box')
            for i,play_danmunum_author in enumerate(plays_danmunum_authors):
                if i == 0:
                    play.append(play_danmunum_author.text)
                elif i == 1:
                    danmu_num.append(play_danmunum_author.text)
                elif i == 2:
                    author.append(play_danmunum_author.text)
                else:
                    continue

for i in range(100):
    tmp = {"排名":rank[i],"标题":title[i],"链接":href[i],"播放量":play[i],"弹幕数量":danmu_num[i],"作者":author[i],"ChatId":cid[i],"弹幕":danmu[i]}
    data = data.append(tmp,ignore_index=True)
data.to_csv(path+"bilbili_top100.csv")
browser.close()
