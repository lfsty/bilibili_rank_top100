import pandas as pd
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from ast import literal_eval
from snownlp import SnowNLP
from tqdm import tqdm
import os
import sys

path_data = "./data/bilbili_top100.csv"
path_img = "./data/bilibili_img.jpg"
path_img_result = "./output/bilibili_img_WordCloud.jpg"
path_font = './Font/Adobe-FangSong-Std-R-2.otf'
path_hist = "./output/bilibili_sentiment_hist.jpg"

def generate_wordcloud(danmu_list,path = path_img_result):
    #jieba分词出的弹幕列表
    danmu_jieba_list = list(jieba.cut(" ".join(danmu_list).encode('utf-8')))
    danmu_jieba_str = " ".join(danmu_jieba_list)

    #生成词云
    os.system("cls")
    print("生成弹幕词云中...")
    wc=WordCloud(font_path=path_font,background_color='white',mask=plt.imread(path_img)).generate(danmu_jieba_str)
    wc.to_file(path)
    print("弹幕词云生成完毕")

def analysis_sentiment(danmu_list,path = path_hist):
    #情感倾向值的列表
    sentiment = []
    os.system("cls")
    print("弹幕情感分析中...")

    pbar = tqdm(total=len(danmu_list))

    for sentence in danmu_list:
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
    plt.savefig(path)


if __name__ == '__main__':
    folder = os.path.exists("./output")
    if not folder:
        os.makedirs("./output")

    if os.path.exists(path_data):
        data = pd.read_csv(path_data)
    else:
        print("数据文件不存在！")
        sys.exit()
    danmu_origin_list = []
    danmu_list = []
    #生成原始的弹幕列表和删除两个及以上的连续“啊”和“哈”之后的弹幕列表
    for tmp in data["弹幕"]:
        danmu_origin_list.extend(literal_eval(tmp))

    for tmp in danmu_origin_list:
        if  re.match(r"[\s\S]*[哈啊]{2,}",tmp) == None:  # 如果正则匹配出的数据为None, 就将此数据添加到新列表中
            danmu_list.append(tmp)

    generate_wordcloud(danmu_list)
    analysis_sentiment(danmu_list)
