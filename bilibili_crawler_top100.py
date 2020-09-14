from selenium import webdriver
from bs4 import BeautifulSoup
from pandas import DataFrame as df
import pandas
import requests
import re
import time
import sys
import os
from bilibili_api import video
from tqdm import tqdm

url_rank = "https://www.bilibili.com/ranking"
url_login = "https://passport.bilibili.com/login"
path = "./"
data = df([])

#从视频链接中提取BV号
def getBvid(url):
    bvid_pattern = re.compile(r"BV[0-9a-zA-Z]{10}")
    bvid = bvid_pattern.search(url).group(0)
    return bvid

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

#获得视频信息的字典
def getInfo(url,rank):
    bvid = getBvid(url)
    video_info = video.get_video_info(bvid=bvid)
    #获取视频cid
    cid = video_info["cid"]
    #弹幕
    danmu = getDanmu(cid)
    #标题
    title = video_info["title"]
    #播放量
    play = video_info["stat"]["view"]
    #弹幕数量
    danmu_num = video_info["stat"]["danmaku"]
    #作者
    author = video_info["owner"]["name"]
    info = {"排名":rank,"标题":title,"链接":url,"播放量":play,"弹幕数量":danmu_num,"作者":author,"ChatId":cid,"弹幕":danmu}
    return info


browser = webdriver.Chrome()
browser.implicitly_wait(1)

browser.get(url_login)
input("请在弹出的浏览器中登录您的账号，再返回按回车键继续")
if browser.current_url == url_login:
    print("登录失败，程序退出")
    sys.exit()
else:
    print("登录成功")

time.sleep(5)
os.system("cls")

browser.get(url_rank)
source = browser.page_source.encode("utf-8")

soup = BeautifulSoup(source,'html.parser')
items = soup.find_all(class_='rank-item')
print("爬取视频信息中...")
pbar = tqdm(total=100)

#获取排行榜信息
for item in items:
    #排名
    rank = item.get("data-rank")
    infos = item.find_all(class_='info')
    for info in infos:
        #超链接和标题的class
        hrefs_titles = info.find_all(class_="title")
        for href_title in hrefs_titles:
            #超链接
            url_video = href_title.get('href')
            info = getInfo(url=url_video,rank = rank)
            data = data.append(info,ignore_index=True)
            pbar.update(1)

data.to_csv(path+"bilbili_top100.csv")
browser.close()
