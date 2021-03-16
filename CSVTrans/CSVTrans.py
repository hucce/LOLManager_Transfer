import pandas as pd
import numpy as np
import re
import csv
import time
import os
import requests

#브라우저 제어
from selenium import webdriver
#페이지 로드
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup as bs

def DFinText(baseDF, textCol, txtList):
    txt = ''
    for i in baseDF.index:
        #세로, 가로
        txt += baseDF.iat[i, textCol] + '\n'
        if len(txt) >= 4900 or len(baseDF) == i+1:
            txtList.append(txt)
            txt = ''

def LoadGoogle(baseDF, language, txt, col, startIndex):
    driver = webdriver.Chrome('./chromedriver')

    #기본 구글 번역 url 설정
    loadUrl = 'https://translate.google.com/?hl=ko&sl=auto&tl=[lan]&op=translate'
    base_url = loadUrl.replace('[lan]', language)
    driver.get(base_url)

    time.sleep(0.5)
    input_box = driver.find_element_by_xpath('//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[1]/span/span/div/textarea')
    input_box.send_keys(txt)
    time.sleep(1)
    result = driver.find_element_by_css_selector("#yDmH0d > c-wiz > div > div.WFnNle > c-wiz > div.OlSOob > c-wiz > div.ccvoYb > div.AxqVh > div.OPPzxe > c-wiz.P6w8m.BDJ8fb.BLojaf > div.dePhmb > div > div.J0lOec > span.VIiyi > span > span").text
    #result = result.text.replace('\n', '')
    resultSplit = result.split('\n')

    for txt in resultSplit:
        baseDF.iat[startIndex, col] = txt
        startIndex += 1

    driver.close()

#불러올 데이터들
loadList = []
#일본어, 중국어간체, 중국어번체, 베트남어, 독일어, 러시아어, 스페인어, 아랍어, 이탈리아어, 말레이어, 태국어, 터키어, 프랑스어, 인도네시아어, 자바어, 뱅골어, 힌디어, 포르투칼어
#Japanese, Simplified Chinese, Traditional Chinese, Vietnamese, German, Russian, Spanish, Arabic, Italian, Malay, Thai, Turkish, French, Indonesian, Javanese, Bengali, Hindi, Portuguese
languageList = ['ja', 'CN', 'TW', 'vi', 'de', 'ru', 'es', 'ar', 'it', 'ms', 'th', 'tr', 'fr', 'id', 'jw', 'bn', 'hi', 'pt']

#데이터 불러오기
read = pd.read_csv('./English/Script.csv', encoding = 'utf-8')
#Name, Dec
colList = ['Name', 'Dec']
for col in colList:
    for dfCol in read.columns:
        if dfCol in col:
            txtList = []
            DFinText(read, col, txtList)
            startIndex = 0
            for txt in txtList:
                LoadGoogle(read, 'ja', txt, col, startIndex)

read.to_csv('./ReplacePlayer.csv', mode='w', index=False, encoding='utf-8')

print(read)