import pandas as pd
import os
from translate import Translator 

def translate_text(text):
    try:
        translated = translator.translate(text)
        return translated
    except Exception as e:
        return str(e)

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
 
def Convert(loadList, languageFull, replaceList):
    for loadFile in loadList:
        
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
                colList = ['Name', 'Dec']
                for col in colList:
                    for dfCol in result.columns:
                        # column 확인
                        if col in dfCol:
                            result[col] = result[col].apply(translate_text)

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
            colList = ['Name', 'Dec']
            for col in colList:
                for dfCol in current_read.columns:
                    # column 확인
                    if col in dfCol:
                        current_read[col] = current_read[col].apply(translate_text)
            
            createFolder('./' + languageFull)
            current_read.to_csv('./'+ languageFull +'/' + loadFile + '.csv', mode='w', index=False, encoding='utf-8-sig')

        print(languageFull + ' ' + loadFile)

#불러올 데이터들
loadList = ['AccountBox', 'Etc', 'MatchCategory', 'MatchItem', 'Notice', 'Script', 'ShopItem', 'Tutorial']

#완전히 새로운 데이터로 변경
replaceList = ['AccountBox', 'Etc', 'MatchCategory', 'MatchItem', 'Notice', 'Script', 'ShopItem', 'Tutorial']

#일본어, 중국어간체, 중국어번체, 베트남어, 독일어, 러시아어, 스페인어, 아랍어, 이탈리아어, 말레이어, 태국어, 터키어, 프랑스어, 인도네시아어, 자바어, 뱅골어, 힌디어, 포르투칼어
#Japanese, Simplified Chinese, Traditional Chinese, Vietnamese, German, Russian, Spanish, Arabic, Italian, Malay, Thai, Turkish, French, Indonesian, Javanese, Bengali, Hindi, Portuguese
readLanDF = pd.read_csv('./LanguageList.csv', encoding = 'utf-8')
languageList = ['ja', 'zh-CN', 'zh-TW', 'vi', 'de', 'ru', 'es', 'ar', 'it', 'ms', 'th', 'tr', 'fr', 'id', 'jw', 'bn', 'hi', 'pt']

for lan in range(0, len(languageList)):
    translator = Translator(from_lang='en', to_lang= languageList[lan])
    Convert(loadList, readLanDF['Language'][lan], replaceList)

for loadFile in loadList:
    originRead = pd.read_csv('./English/' + loadFile + '.csv', encoding = 'utf-8')
    # 비포로
    originRead.to_csv('./BeforeEnglish/' + loadFile + '.csv', mode='w', index=False, encoding='utf-8-sig')