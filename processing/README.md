# Cleansing
- content 데이터만 클렌징
- 특정 문자 제거
- 본문 내용이 20자 미만 행 제거
- 특정 문장(예:사진 영상 제보받습니다)포함 이후 문장 제거
- 상기 과정 등을 거친 후 정규표현식을 활용하여 특수기호 등 제거
- DATE의 format 통일
- 데이터에서 중복 제거
- 기자 이름(3글자)만 추출

<br/>

- 특정문자 제거((),[]포함)
```python
patterns = r'\현지시간|무단 전재 및 재배포 금지|이 기사는 프리미엄 스타트업 미디어 플랫폼 한경 긱스에 게재된 기사입니다'
df100['content'] = df100['content'].apply(lambda x: re.sub(patterns, '', x) if isinstance(x, str) else x)
```
<br/>

- 본문 내용이 20자 미만인 rows 제거
```python
df['content'] = df['content'].apply(lambda x: '' if isinstance(x, str) and len(x.split()) < 20 else x)
```
<br/>

- 특정 문장(예:사진 영상 제보받습니다)포함 이후 모두 제거
```python
f['content'] = df['content'].apply(lambda x: re.sub(r'\[사진 영상 제보받습니다.*\]|■ 제보하기.*', '', x) if isinstance(x, str) else x)
```
<br/>

- 날짜 컬럼 포맷 
```python
# 포맷 통일
df['publication_date'] = df['publication_date'].astype(str)
df['publication_date'] = df['publication_date'].str.replace('_', '.')
df['publication_date'] = df['publication_date'].apply(lambda x: '.'.join(x.split('.')[:3]) if len(x.split('.')) > 2 else x)
```
<br/>

#정규표현식 함수로 특수문자/기호 제거
```python    
    def cleansing_text(text):
        text = re.sub(r'☞[^☞]*', '', text)
        text = re.sub(r'[▲△▷▶▼▽◆◇■=#※ㆍ/·.,;:!?\'"‘’“”~∼&()→%․\[\]\-–]', '', text)
    return text
    df['content'] = df['content'].apply(cleansing_text)
    
```
<br/>

- 중복된 content 제거
```python
# content 중복 갯수 확인
duplicated_contents = df[df.duplicated(subset=['content'], keep=False)]
grouped = duplicated_contents.groupby('content').apply(lambda x: x.index.tolist()).reset_index(name='indices')
num_duplicated_contents = grouped.shape[0]

# content 중복된 행 제거
df.drop_duplicates(subset=['content'], keep='first')
``

