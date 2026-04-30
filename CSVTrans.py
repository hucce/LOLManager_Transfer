import pandas as pd
import re
import csv
import os
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ChromeService, ChromeOptions

PROTECTED_TOKEN_PATTERN = re.compile(r'<[^>]+>|\[\d+\]')


def split_edge_markers(text):
    if not isinstance(text, str) or not text:
        return '', text, ''

    prefix_match = re.match(r'^[^\w\[<]+\s*', text)
    suffix_match = re.search(r'\s*[^\w\]>]+$', text)

    prefix = prefix_match.group(0) if prefix_match else ''
    suffix = suffix_match.group(0) if suffix_match else ''

    start = len(prefix)
    end = len(text) - len(suffix) if suffix else len(text)
    core_text = text[start:end]
    return prefix, core_text, suffix


def protect_inline_tokens(text):
    protected_values = []

    def replacer(match):
        token_index = len(protected_values)
        protected_values.append(match.group(0))
        return f'__PROTECTED_{token_index}__'

    protected_text = PROTECTED_TOKEN_PATTERN.sub(replacer, text)
    return protected_text, protected_values


def restore_inline_tokens(text, protected_values):
    restored_text = text
    for token_index, original_value in enumerate(protected_values):
        restored_text = restored_text.replace(f'__PROTECTED_{token_index}__', original_value)
    return restored_text


def preserve_edge_markers(source_text, translated_text):
    if not isinstance(source_text, str) or not isinstance(translated_text, str):
        return translated_text

    prefix, _, suffix = split_edge_markers(source_text)
    result_text = translated_text.strip()
    if not result_text:
        return translated_text

    if prefix.strip() and not result_text.startswith(prefix.strip()):
        result_text = prefix + result_text.lstrip()

    if suffix.strip() and not result_text.endswith(suffix.strip()):
        result_text = result_text.rstrip() + suffix

    return result_text


def restore_identifier_column(source_df, target_df):
    if 'ID' in source_df.columns and 'ID' in target_df.columns:
        source_id = source_df['ID']
        if pd.api.types.is_numeric_dtype(source_id):
            target_df['ID'] = pd.to_numeric(source_id, errors='coerce').astype('Int64')
        else:
            target_df['ID'] = source_id


def LoadGoogle(txt, driver, extxt):
    if not txt or txt == extxt:
        return extxt

    prefix, core_text, suffix = split_edge_markers(txt)
    if not core_text.strip():
        return txt

    protected_core_text, protected_values = protect_inline_tokens(core_text)
    _time = 0
    result = None
    text = ''

    while True:
        try:
            while True:
                try:
                    input_box = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/div/c-wiz/span/span/div/textarea')
                    break
                except Exception:
                    driver.implicitly_wait(0.1)

            input_box.clear()
            input_box.send_keys(protected_core_text)
            driver.implicitly_wait(0.2)

            while True:
                try:
                    result = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz/div/div[6]/div/div[1]/span[1]')
                    text = result.text.replace('\n', '').replace('\r', '').replace('(남성)', '')
                    text = restore_inline_tokens(text, protected_values)
                    text = preserve_edge_markers(txt, text)
                    if extxt != text and text != '':
                        break
                    if text == '':
                        try:
                            btn = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz/div/div[5]/div[2]/button/span')
                            btn.click()
                        except Exception:
                            pass
                    driver.implicitly_wait(0.1)
                    _time += 0.1
                except Exception:
                    try:
                        btn = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz/div/div[5]/div[2]/button/span')
                        btn.click()
                        driver.implicitly_wait(0.1)
                        _time += 0.1
                    except Exception:
                        try:
                            result = driver.find_element(By.XPATH, '/html/body/c-wiz/div/div[2]/c-wiz/div[2]/c-wiz/div[1]/div[2]/div[2]/c-wiz/div/div[7]/div[1]/div[1]')
                            text = result.text.replace('\n', '').replace('\r', '').replace('(남성)', '')
                            text = restore_inline_tokens(text, protected_values)
                            text = preserve_edge_markers(txt, text)
                            if extxt != text and text != '':
                                break
                            driver.implicitly_wait(0.1)
                            _time += 0.1
                        except Exception:
                            driver.implicitly_wait(0.1)
                            _time += 0.1

                if _time >= 40:
                    if result is not None:
                        text = result.text.replace('\n', '').replace('\r', '').replace('(남성)', '')
                        text = restore_inline_tokens(text, protected_values)
                        text = preserve_edge_markers(txt, text)
                    else:
                        text = txt
                    break
            break
        except Exception:
            print('에러 발생')

    return text

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
 
def Convert(loadList, language, languageFull, replaceList, driver, currentVersion):
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
                    if str(checkList['Version'][i]) == currentVersion:
                        print(languageFull + ' ' + loadFile)
                        checkLanguage = True
                        break
                
        if checkLanguage == False:
            #데이터 불러오기
            originRead = pd.read_csv('./English/' + loadFile + '.csv', encoding = 'utf-8')
            current_read = originRead.copy()

            # 바꿀 데이터인지 확인
            isReplace = False
            for replaceData in replaceList:
                if loadFile == replaceData:
                    isReplace = True
                    break
            
            # 파일이 있어야 비교
            if os.path.isfile('./BeforeEnglish/' + loadFile + '.csv') and isReplace == False:
                before_read = pd.read_csv('./BeforeEnglish/' + loadFile + '.csv', encoding = 'utf-8')
                compare_columns = [
                    col for col in originRead.columns
                    if col in before_read.columns and any(key in col for key in ['Name', 'Dec'])
                ]
                compare_length = min(len(originRead), len(before_read))
                changed_mask = pd.Series(False, index=originRead.index)
                result = originRead.iloc[0:0].copy()

                if compare_length > 0 and compare_columns:
                    current_compare = originRead.iloc[:compare_length][compare_columns].fillna('')
                    before_compare = before_read.iloc[:compare_length][compare_columns].fillna('')
                    changed_mask.iloc[:compare_length] = current_compare.ne(before_compare).any(axis=1).to_numpy()

                if len(originRead) > len(before_read):
                    changed_mask.iloc[compare_length:] = True

                result = originRead.loc[changed_mask].copy()

                if not result.empty:
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
                                    source_text = result.at[r, col]
                                    if exEx == source_text:
                                        result.at[r, col] = exTxt
                                    else:
                                        van = LoadGoogle(source_text, driver, exTxt)
                                        exEx = source_text
                                        result.at[r, col] = van
                                        exTxt = van

                    # 이제 바뀐 애들 것에서 기존꺼를 확인해서 내용을 바꾼다.
                    languageRead = pd.read_csv('./'+ languageFull +'/' + loadFile + '.csv', encoding = 'utf-8')
                    languageRead = languageRead.reindex(originRead.index).copy()
                    setColList = ['Name', 'Dec']
                    for _index in result.index:
                        for col in setColList:
                            for dfCol in languageRead.columns:
                                if col in dfCol:
                                    languageRead.at[_index, dfCol] = result.at[_index, col]
                                    break
                    # 저장한다
                    languageRead = languageRead.iloc[:len(originRead)]
                    restore_identifier_column(originRead, languageRead)
                    if loadFile == 'Etc':
                        languageRead['Korean'] = originRead['Korean'] 
                    createFolder('./' + languageFull)
                    languageRead.to_csv('./'+ languageFull +'/' + loadFile + '.csv', mode='w', index=False, encoding='utf-8-sig')
            else:
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

                restore_identifier_column(originRead, current_read)
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
replaceList = ['Notice']

#현재 버전
currentVersion = '8.23'

#일본어, 중국어간체, 중국어번체, 베트남어, 독일어, 러시아어, 스페인어, 아랍어, 이탈리아어, 말레이어, 태국어, 터키어, 프랑스어, 인도네시아어, 자바어, 뱅골어, 힌디어, 포르투칼어
#Japanese, Simplified Chinese, Traditional Chinese, Vietnamese, German, Russian, Spanish, Arabic, Italian, Malay, Thai, Turkish, French, Indonesian, Javanese, Bengali, Hindi, Portuguese
readLanDF = pd.read_csv('./LanguageList.csv', encoding = 'utf-8')
originLanguageList = ['en','ko','zh-CN','zh-TW','de','fr','es','it','pt','tr','ru','ja','vi','ms','th','id','jw','bn','hi','ar']
languageList = ['ja', 'zh-CN', 'zh-TW', 'vi', 'de', 'ru', 'es', 'ar', 'it', 'ms', 'th', 'tr', 'fr', 'id', 'jw', 'bn', 'hi', 'pt']

chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

for lan in range((len(readLanDF) - len(languageList)), len(readLanDF)):
    Convert(loadList, languageList[lan], readLanDF['Language'][lan], replaceList, driver, currentVersion)

driver.quit()

for loadFile in loadList:
    originRead = pd.read_csv('./English/' + loadFile + '.csv', encoding = 'utf-8')
    createFolder('./BeforeEnglish/')
    # 비포로
    originRead.to_csv('./BeforeEnglish/' + loadFile + '.csv', mode='w', index=False, encoding='utf-8-sig')