# Crawler

## 환경설정
<aside>
<b>수집 기간</b>
<br/>
2024.08.01 ~ 2024.08.31 (1개월)
</aside>
<br/>
<aside>
<b>사용 언어</b>
<br/>
Python 3.11
</aside>

<br/>
<br/>

## 크롤링

### 1. 뉴스기사
- 카테고리ID, 세부카테고리, 언론사명, 제목, 작성자, 작성일시, 수정일시, 본문내용, 링크, 댓글 수집
#### 네이버 뉴스
- 113,124건이며 동적 크롤링 방식 사용
- 카테고리(Category): 경제
- 세부카테고리(subcategory):금융/증권/산업&재계/중기&벤처/부동산/글로벌/생활경제/경제일반
#### 다음 뉴스
- 69,083건이며 동적 크롤링 방식 사용
- 카테고리(Category): 경제/사회
- 경제 세부카테고리(subcategory):금융/산업/취업/고용/자동차/주식/부동산/소비자/국제경제
- 사회 세부카테고리(subcategory):사건&사고/교육/미디어/성평등/인권/복지/노동/환경/전국
<br/>

- 크롤링 할 세부카테고리와 이름 매핑
```python
category_mapping = {
    '259': '금융',
    '258': '증권',
    '261': '산업/제계',
    '771': '중기/벤처',
    '260': '부동산',
    '262': '글로벌 경제',
    '310': '생활경제',
    '263': '경제일반'
}
```
<br/>

- URL에서 카테고리 코드를 추출하고, 카테고리 이름 반환
```python
def get_category_from_url(url):
    category_id = url.split('/')[-1].split('?')[0]  
    return category_mapping.get(category_id, '기타')  
```
<br/>

- 크롤링할 날짜 선정
```python
start_date = '20240801'
end_date = '20240831'
date_range = generate_date_range(start_date, end_date)
```
<br/>

- 제목 추출
```python
title = soup_in.find('h2').text if soup_in.find('h2') else '제목 오류'
```
<br/>

- 작성일시 추출
```python
date = soup_in.find('span', {"class": "media_end_head_info_datestamp_time _ARTICLE_DATE_TIME"}).
text if soup_in.find('span', {"class": "media_end_head_info_datestamp_time _ARTICLE_DATE_TIME"}) else '날짜 오류'
```
<br/>

- 본문내용 추출
```python
content = soup_in.find('article', {"id": "dic_area"}).text if soup_in.find('article', {"id": "dic_area"}) else '본문 오류'
```
<br/>

- 작성자 추출
```python
author = '기자명 오류'
if soup_in.find('em', {"class": "media_end_head_journalist_name"}):
    author = soup_in.find('em', {"class": "media_end_head_journalist_name"}).text
elif soup_in.find('span', {"class": "byline_s"}):
    author = soup_in.find('span', {"class": "byline_s"}).text[:3] + " 기자"
```
<br/>

- 크롬 드라이버 설정 및 크롤링 실행
```python
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)
```
<br/>

- 페이지 끝까지 스크롤하여 콘텐츠 로드
```python
def scroll_to_bottom(driver, pause_time=1):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            try:
                more_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div > div.section_more > a"))
                )
                more_button.click()
                time.sleep(pause_time)
            except Exception as e:
                print(f"더보기 버튼 클릭 오류: {e}")
                break
        
        last_height = new_height
```

<br/>

- 수집한 데이터를 CSV 파일로 저장하는 함수
```python
def save_to_csv(start_date, end_date, all_scraped_data):
    """스크래핑한 데이터를 CSV 파일로 저장하는 함수"""
    # 파일 이름 생성
    file_name_articles = f"{start_date}-{end_date}_articles.csv"
    file_name_comments = f"{start_date}-{end_date}_comments.csv"

