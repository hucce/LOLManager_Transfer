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
from tqdm import tqdm

def LoadGoogle(txt, driver, extxt):
    _time = 0
    while(True):
        try:
            while(True):
                try:
                    input_box = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/div/c-wiz/span/span/div/textarea')
                    break
                except:
                    driver.implicitly_wait(0.1)
            
            input_box.clear()
            input_box.send_keys(txt)
            result = ''

            while(True):
                try:
                    result = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz/div/div[6]/div/div[1]/span[1]')
                    if (extxt != result.text and '' != result.text):
                        text = result.text
                        break
                    elif('' == result.text):
                        try:
                            #번역 에러
                            btn = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz/div/div[5]/div[2]/button/span')
                            btn.click()
                            driver.implicitly_wait(0.1)
                            _time += 0.1
                        except:
                            driver.implicitly_wait(0.1)
                            _time += 0.1
                    else:
                        driver.implicitly_wait(0.1)
                        _time += 0.1
                except:
                    try:
                        #번역 에러
                        btn = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz/div/div[5]/div[2]/button/span')
                        btn.click()
                        driver.implicitly_wait(0.1)
                        _time += 0.1
                    except:
                        try:
                            result = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz/div/div[7]/div[1]/div[1]')
                            if (extxt != result.text and '' != result.text):
                                text = result.text
                                break
                            elif('' == result.text):
                                try:
                                    #번역 에러
                                    btn = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz/div/div[5]/div[2]/button/span')
                                    btn.click()
                                    driver.implicitly_wait(0.1)
                                    _time += 0.1
                                except:
                                    driver.implicitly_wait(0.1)
                                    _time += 0.1
                            else:
                                driver.implicitly_wait(0.1)
                                _time += 0.1

                            driver.implicitly_wait(0.1)
                            _time += 0.1
                        except:
                            driver.implicitly_wait(0.1)
                            _time += 0.1
                if _time >= 40:
                    text = result.text
                    break
            break
        except:
            print("에러 발생")

    return text

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
 
def Convert(loadList, language, languageFull, replaceList, dirver, currentVersion):
    # 체크리스트 불러오기
    if os.path.isfile('./checkList.csv'):
        checkList = pd.read_csv('./checkList.csv', encoding = 'utf-8')
    else:
        checkList = pd.DataFrame(columns=['Language', 'File'])
    
    for loadFile in loadList:
        checkLanguage = False
        # 체크리스트
        for i in range(len(checkList)):
            if  checkList['Language'][i] == languageFull:
                if checkList['File'][i] == loadFile:
                    if checkList['Version'][i] == currentVersion:
                        print(languageFull + ' ' + loadFile)
                        checkLanguage = True
                        break
                
        if checkLanguage == False:
            #데이터 불러오기
            originRead = pd.read_csv('./English/' + loadFile + '.csv', encoding = 'utf-8')
            current_read = originRead

            # 바꿀 데이터인지 확인
            isReplace = False
            for replaceData in replaceList:
                if loadFile == replaceData:
                    isReplace = True
                    break
            
            # 파일이 있어야 비교
            if os.path.isfile('./BeforeEnglish/' + loadFile + '.csv') and isReplace == False:
                before_read = pd.read_csv('./BeforeEnglish/' + loadFile + '.csv', encoding = 'utf-8')
                
                # 중복 체크
                # 데이터프레임 병합하여 차이점 표시
                df_diff = originRead.merge(before_read, how='outer', indicator=True)

                # 첫 번째 데이터프레임에만 있는 행 필터링
                result = df_diff[df_diff['_merge'] == 'left_only'].drop(columns=['_merge'])

                # 중복을 뺐는데도 남아 있는 내용이 있다면
                if result.empty == False:
                    #기본 구글 번역 url 설정
                    loadUrl = 'https://translate.google.com/?hl=ko&sl=auto&tl=[lan]&op=translate'
                    base_url = loadUrl.replace('[lan]', language)
                    driver.get(base_url)

                    colList = ['Name', 'Dec']
                    exTxt = ''
                    exEx = ''
                    for col in colList:
                        for dfCol in result.columns:
                            # column 확인
                            if col in dfCol:
                                for r in result.index:
                                    if exEx == current_read.at[r, col]:
                                        result.at[r, col] = exTxt
                                    else:
                                        van = LoadGoogle(result.at[r, col], driver, exTxt)
                                        exEx = current_read.at[r, col]
                                        result.at[r, col] = van
                                        exTxt = van

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
                    languageRead = languageRead.iloc[:len(originRead)]
                    if loadFile == 'Etc':
                        languageRead['Korean'] = originRead['Korean'] 
                    createFolder('./' + languageFull)
                    languageRead.to_csv('./'+ languageFull +'/' + loadFile + '.csv', mode='w', index=False, encoding='utf-8-sig')
            else:
                #기본 구글 번역 url 설정
                loadUrl = 'https://translate.google.com/?hl=ko&sl=auto&tl=[lan]&op=translate'
                base_url = loadUrl.replace('[lan]', language)
                driver.get(base_url)

                colList = ['Name', 'Dec']
                exTxt = ''
                exEx = ''
                for col in colList:
                    for dfCol in current_read.columns:
                        # column 확인
                        if col in dfCol:
                            for r in tqdm(current_read.index):
                                if exEx == current_read.at[r, col]:
                                    current_read.at[r, col] = exTxt
                                else:
                                    van = LoadGoogle(current_read.at[r, col], driver, exTxt)
                                    exEx = current_read.at[r, col]
                                    current_read.at[r, col] = van
                                    exTxt = van
                
                createFolder('./' + languageFull)
                current_read.to_csv('./'+ languageFull +'/' + loadFile + '.csv', mode='w', index=False, encoding='utf-8-sig')

            # 체크리스트에 추가
            new_data = pd.DataFrame({'Language': [languageFull], 'File': [loadFile], 'Version': [currentVersion]})
            checkList = pd.concat([checkList, new_data], ignore_index=True)
            checkList.to_csv('./checkList.csv', mode='w', index=False, encoding='utf-8-sig')
            print(languageFull + ' ' + loadFile)

def CsvNRemove(loadFile, languageFull):
    # 원본 CSV 파일 경로와 저장할 파일 경로
    file_path = './'+ languageFull +'/' + loadFile + '.csv'

    # CSV 파일 덮어쓰기
    with open(file_path, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        rows = [
            [cell.replace('\n', ' ').replace('\r', ' ').replace('(남성)', ' ') for cell in row]
            for row in reader
        ]

    # 수정된 내용을 다시 같은 파일에 저장 (덮어쓰기)
    with open(file_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)

#불러올 데이터들
loadList = ['AccountBox', 'Etc', 'MatchCategory', 'MatchItem', 'Notice', 'Script', 'ShopItem', 'Tutorial']

#완전히 새로운 데이터로 변경
replaceList = ['AccountBox', 'Etc', 'MatchCategory', 'MatchItem', 'Notice', 'Script', 'ShopItem', 'Tutorial']
replaceList = ['Notice']
replaceList = ['Script']

#현재 버전
currentVersion = '6.6'

#일본어, 중국어간체, 중국어번체, 베트남어, 독일어, 러시아어, 스페인어, 아랍어, 이탈리아어, 말레이어, 태국어, 터키어, 프랑스어, 인도네시아어, 자바어, 뱅골어, 힌디어, 포르투칼어
#Japanese, Simplified Chinese, Traditional Chinese, Vietnamese, German, Russian, Spanish, Arabic, Italian, Malay, Thai, Turkish, French, Indonesian, Javanese, Bengali, Hindi, Portuguese
readLanDF = pd.read_csv('./LanguageList.csv', encoding = 'utf-8')
originLanguageList = ['en','ko','zh-CN','zh-TW','de','fr','es','it','pt','tr','ru','ja','vi','ms','th','id','jw','bn','hi','ar']
languageList = ['ja', 'zh-CN', 'zh-TW', 'vi', 'de', 'ru', 'es', 'ar', 'it', 'ms', 'th', 'tr', 'fr', 'id', 'jw', 'bn', 'hi', 'pt']

for lan in range((len(readLanDF) - len(languageList)), len(readLanDF)):
    for load in loadList:
        CsvNRemove(load, readLanDF['Language'][lan])
        print('Remove ' + readLanDF['Language'][lan] + ' ' + load)