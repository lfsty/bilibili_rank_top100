import pandas as pd
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from ast import literal_eval
from snownlp import SnowNLP
from tqdm import tqdm
import os

path_data = "./data/bilbili_top100.csv"
path_img = "./data/bilibili_img.jpg"
path_img_result = "./output/bilibili_img_result.jpg"
path_font = './Font/Adobe-FangSong-Std-R-2.otf'
path_hist = "./output/bilibili_sentiment_hist.jpg"

folder = os.path.exists("./output")
if not folder:
    os.makedirs("./output")

data = pd.read_csv(path_data)
danmu = ""

#弹幕以句号分隔，删除两个及以上的连续“啊”和“哈”
for tmp in data["弹幕"]:
    danmu += "。".join(literal_eval(tmp))
danmu = re.sub(r"(哈){2,}","",danmu)
danmu = re.sub(r"(啊){2,}","",danmu)

#jieba分词出的弹幕列表
danmu_jieba_list = list(jieba.cut(danmu.encode('utf-8')))
danmu_jieba_str = " ".join(danmu_jieba_list)

#生成词云
os.system("cls")
print("生成弹幕词云中...")
wc=WordCloud(font_path=path_font,background_color='white',mask=plt.imread(path_img)).generate(danmu_jieba_str)
wc.to_file(path_img_result)
print("弹幕词云生成完毕")

#情感倾向值的列表
sentiment = []
#弹幕用snownlp分词出的结果
sn = SnowNLP(danmu)
os.system("cls")
print("弹幕情感分析中...")

pbar = tqdm(total=len(sn.sentences))

for sentence in sn.sentences:
    tmp = SnowNLP(sentence)
    sentiment.append(round(float(tmp.sentiments),2))
    pbar.update(1)

pbar.close()
print("弹幕情感分析完毕")

#生成弹幕情感指数的直方图
plt.hist(x = sentiment,bins = 21)
plt.xticks([0,0.2,0.4,0.5,0.6,0.8,1])
plt.xlabel("Positive emotional orientation")
plt.ylabel("Number")
plt.savefig(path_hist)