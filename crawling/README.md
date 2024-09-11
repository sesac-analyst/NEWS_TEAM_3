# 크롤링 코드
# Cleansing
- content 데이터만 클렌징
- 데이터에서 중복 제거
- 괄호()안의 10자 미만 문자 삭제(done)
- []안의 내용 제거(done)
- [사진 영상 제보받습니다]포함 이후 문장 제거(done)
- 상기 과정을 거친 후 정규표현식을 활용하여 데이터 클렌징
- DATE의 데이터 통일

<br/>

- 날짜 컬럼 포맷 
```python
# 포맷 통일
df['publication_date'] = df['publication_date'].astype(str)
df['publication_date'] = df['publication_date'].str.replace('_', '.')
df['publication_date'] = df['publication_date'].apply(lambda x: '.'.join(x.split('.')[:3]) if len(x.split('.')) > 2 else x)
```
<br/>

#정규표현식 함수로 기본적인 문자/기호 제거
def cleansing_text(text):
    
    # 특수 기호 및 광고성 텍스트 제거
    text = re.sub(r'☞[^☞]*', '', text)
    
    # 구두점, 따옴표, 기타 특수 문자 제거
    text = re.sub(r'[▲△▷▶▼▽◆◇■=#※ㆍ/·.,;:!?\'"‘’“”~∼&()→%․\[\]\-–]', '', text)
    
    return text
    
df['content'] = df['content'].apply(cleansing_text)
```python

```
<br/>
<br/>

### 2. content
- 중복된 컬럼 제거(content)
```python
# content 중복 갯수 확인
duplicated_contents = df[df.duplicated(subset=['content'], keep=False)]
grouped = duplicated_contents.groupby('content').apply(lambda x: x.index.tolist()).reset_index(name='indices')
num_duplicated_contents = grouped.shape[0]

# 중복된 제목의 인덱스를 그룹화하여 중복 관계를 표시
duplicate_groups = duplicate_titles.groupby('제목').apply(lambda x: x.index.tolist())

# content 중복된 행 제거
df.drop_duplicates(subset=['content'], keep='first')

# 중복된 행 제거 후 중복 갯수확인
duplication_counts = df['content'].value_counts()
duplicated_counts = duplication_counts[duplication_counts > 1]
duplicated_counts

# 기자 이름(3글자)만 추출
df['author'] = df['author'].apply(lambda text: re.match(r'^[가-힣]{3}', str(text)).group(0) if re.match(r'^[가-힣]{3}', str(text)) else text)

``
<br/>

