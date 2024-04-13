from asyncore import read
from pickle import FALSE
from tabnanny import check
from tkinter.tix import Tree
#from selectors import EpollSelector
import pandas as pd
import numpy as np
import re
import csv
import time
import os
import requests

#브라우저 제어
from selenium import webdriver
from selenium.webdriver.common.by import By
#페이지 로드
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup as bs
from selenium.webdriver import Chrome

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ChromeService, ChromeOptions

def DFinText(baseDF, textCol, txtList):
    txt = ''
    check = 0
    for i in baseDF.index:
        #세로, 가로
        txt += str(baseDF[textCol][i]) + '{{{}}}\n\n'
        if len(txt) >= 4900 or len(baseDF) == check+1:
            txtList.append(txt)
            txt = ''
        check += 1

def LoadGoogle(baseDF, startIndex, language, txt, col):
    options = ChromeOptions()
    options.add_argument('--headless')

    service = ChromeService(ChromeDriverManager().install())

    with Chrome(options=options, service=service) as driver:
        print(service.path) # this is where the driver is located

    driver = webdriver.Chrome()

    #기본 구글 번역 url 설정
    loadUrl = 'https://translate.google.com/?hl=ko&sl=auto&tl=[lan]&op=translate'
    base_url = loadUrl.replace('[lan]', language)
    driver.get(base_url)

    time.sleep(3)
    input_box = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[1]/span/span/div/textarea')
    input_box.send_keys(txt)
    result = ''

    while(True):
        try:
            result = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[2]/div/div[6]/div/div[1]/span[1]')
            result = result.text
            break
            
        except:
            time.sleep(0.1)

    result = result.replace('\n', '')
    resultSplit = result.split('{{{}}}')

    max = len(resultSplit)
    if resultSplit[max-1] == '':
        max = max -1

    for index in range(startIndex, (max + startIndex)):
        baseDF.at[index, col] = resultSplit[index - startIndex]

    driver.close()

    return max + startIndex

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
 
def Convert(loadList, language, languageFull):
    for loadFile in loadList:
        #데이터 불러오기
        originRead = pd.read_csv('./English/' + loadFile + '.csv', encoding = 'utf-8')
        current_read = originRead

        # 파일이 있어야 비교
        if os.path.isfile('./BeforeEnglish/' + loadFile + '.csv'):
            before_read = pd.read_csv('./BeforeEnglish/' + loadFile + '.csv', encoding = 'utf-8')
            
            # 중복 체크
            result = pd.concat([current_read, before_read]).drop_duplicates(keep=False)
            result = result[~result.index.duplicated(keep='first')]

            # 중복을 뺐는데도 남아 있는 내용이 있다면
            if result.empty == False:
                colList = ['Name', 'Dec']
                for col in colList:
                    for dfCol in result.columns:
                        # column 확인
                        if col in dfCol:
                            # 있다면
                            # 바뀐 내용중에서 최신 내용만 가져온다.
                            txtList = []
                            DFinText(result, col, txtList)
                            startIndex = 0
                            for txt in txtList:
                                startIndex = LoadGoogle(result, startIndex, language, txt, col)

                # 이제 바뀐 애들 것에서 기존꺼를 확인해서 내용을 바꾼다.
                languageRead = pd.read_csv('./'+ languageFull +'/' + loadFile + '.csv', encoding = 'utf-8')
                setColList = ['ID', 'Name', 'Dec']
                for _index in result.index:
                    for col in setColList:
                        for dfCol in languageRead.columns:
                            if col in dfCol:
                                languageRead.at[_index, dfCol] = result.at[_index, col]
                                break
                # 저장한다
                createFolder('./' + languageFull)
                languageRead.to_csv('./'+ languageFull +'/' + loadFile + '.csv', mode='w', index=False, encoding='utf-8-sig')
        else:
            if os.path.isfile('./'+ languageFull +'/' + loadFile + '.csv'):
                print('파일 있음')
            else:
                colList = ['Name', 'Dec']
                for col in colList:
                    for dfCol in current_read.columns:
                        # column 확인
                        if col in dfCol:
                            # 있다면
                            # 바뀐 내용중에서 최신 내용만 가져온다.
                            txtList = []
                            DFinText(current_read, col, txtList)
                            startIndex = 0
                            for txt in txtList:
                                index = LoadGoogle(current_read, startIndex, language, txt, col)
                                startIndex = index
                
                createFolder('./' + languageFull)
                current_read.to_csv('./'+ languageFull +'/' + loadFile + '.csv', mode='w', index=False, encoding='utf-8-sig')

        print(languageFull + ' ' + loadFile)

def ConvertLanguage():
    readLanDF = pd.read_csv('./language.csv', encoding = 'utf-8')
    readLanDF['Convert'] = 'a'
    for lan in range(0, len(readLanDF)):
        driver = webdriver.Chrome('./chromedriver')

        #기본 구글 번역 url 설정
        loadUrl = 'https://translate.google.com/?hl=ko&sl=auto&tl=[lan]&op=translate'
        base_url = loadUrl.replace('[lan]', readLanDF['Lan'][lan])
        driver.get(base_url)

        time.sleep(0.5)
        input_box = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz[1]/span/span/div/textarea')
        input_box.send_keys(readLanDF['Language'][lan])
        time.sleep(2.5)
        result = ''
        try:
            result = driver.find_element(By.CSS_SELECTOR, "#yDmH0d > c-wiz > div > div.WFnNle > c-wiz > div.OlSOob > c-wiz > div.ccvoYb > div.AxqVh > div.OPPzxe > c-wiz.P6w8m.BDJ8fb.BLojaf > div.dePhmb > div > div.J0lOec > span.VIiyi").text
        except:
            try:
                result = driver.find_element(By.CSS_SELECTOR, "#yDmH0d > c-wiz > div > div.WFnNle > c-wiz > div.OlSOob > c-wiz > div.ccvoYb > div.AxqVh > div.OPPzxe > c-wiz.P6w8m.BDJ8fb > div.dePhmb > div > div.J0lOec > span.VIiyi > span > span").text
            except:
                print("결과를 제대로 크롤링 못했음")
        
        readLanDF['Convert'][lan] = result

        driver.close()

    readLanDF.to_csv('./languageConvert.csv', mode='w', index=False, encoding='utf-8-sig')

def GetDifferences(df1, df2):
  df = pd.concat([df1, df2]).reset_index(drop=True)
  idx = [diff[0] for diff in df.groupby(list(df.columns)).groups.values() if len(diff) == 1]
  return df.reindex(idx)

#불러올 데이터들
#loadList = ['AccountBox', 'Etc', 'MatchCategory', 'MatchItem', 'Notice', 'Player', 'Script', 'ShopItem', 'Tutorial', 'Team', 'Store']
loadList = ['AccountBox', 'Etc', 'MatchCategory', 'MatchItem', 'Notice', 'Script', 'ShopItem', 'Tutorial']
#notReplaceList = ['Team', 'Player', 'Coach', 'Store']

#일본어, 중국어간체, 중국어번체, 베트남어, 독일어, 러시아어, 스페인어, 아랍어, 이탈리아어, 말레이어, 태국어, 터키어, 프랑스어, 인도네시아어, 자바어, 뱅골어, 힌디어, 포르투칼어
#Japanese, Simplified Chinese, Traditional Chinese, Vietnamese, German, Russian, Spanish, Arabic, Italian, Malay, Thai, Turkish, French, Indonesian, Javanese, Bengali, Hindi, Portuguese
readLanDF = pd.read_csv('./LanguageList.csv', encoding = 'utf-8')
languageList = ['ja', 'zh-CN', 'zh-TW', 'vi', 'de', 'ru', 'es', 'ar', 'it', 'ms', 'th', 'tr', 'fr', 'id', 'jw', 'bn', 'hi', 'pt']

for lan in range(0, len(languageList)):
    Convert(loadList, languageList[lan], readLanDF['Language'][lan])

for loadFile in loadList:
    originRead = pd.read_csv('./English/' + loadFile + '.csv', encoding = 'utf-8')
    # 비포로
    originRead.to_csv('./BeforeEnglish/' + loadFile + '.csv', mode='w', index=False, encoding='utf-8-sig')
