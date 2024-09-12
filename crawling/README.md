크롤링 코드
# Crawler

## 환경설정
<aside>
<b>수집할 기간</b>
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
- 카테고리ID, 소카테고리, 언론사명, 제목, 작성자, 작성일시, 수정일시, 본문내용, 링크 수집
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

- 크롤링 할 세부카테고리
```python
# 카테고리 코드와 이름 매핑
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

- 본문내용 추출
```python
content = soup_in.find('article', {"id": "dic_area"}).text if soup_in.find('article', {"id": "dic_area"}) else '본문 오류'
```
<br/>

- 위
```python
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(crawl_page, range(1, pages + 1))
```


<br/>

- 날짜 

<br/>

- 
```python
def get_monthly_date_ranges(start_date, end_date):
    date_ranges = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + relativedelta(months=1) - timedelta(days=1), end_date)
        date_ranges.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)
    return date_ranges
```
<br/>

- 
```python
def fetch_url_with_retries(url, headers, retries=10, timeout=10):
    for i in range(retries):
        try:
            # print(f"{datetime.now()} - Attempt {i+1} to fetch URL: {url}")
            res = requests.get(url, headers=headers, timeout=timeout)
            if res.status_code == 200:
                return res
            else:
                print(f"Unexpected status code {res.status_code} for URL: {url}")
        except requests.exceptions.RequestException as e:
            print(f"{datetime.now()} - Request failed ({i+1}/{retries}): {e}")
            sleep(2)
    print(f"{datetime.now()} - Failed to retrieve JSON data from {url}")
    return None
```
<br/>

- 
```python
def clean_filename(filename):
    filename = re.sub(r'[\/:*?"<>|.]', '_', filename)
    filename = re.sub(r'_+', '_', filename)
    return filename.strip('_')
```
<br/>

- 
```python
news_title = crawling_soup.select_one('h1.tit').text.strip()

news_date = crawling_soup.select_one('.txt-copyright > span.date').text.strip()[:10].replace("/", ".")

# 모든 p 태그를 찾아 리스트로 저장
p_tags = crawling_soup.find("article", class_="story-news").find_all('p')
# 뒤에서 두 번째까지 제거한 후, 각 p 태그의 텍스트를 추출하여 하나의 문자열로 결합
if len(p_tags) > 2:
    p_tags = p_tags[:-1]
contents = " ".join([p.get_text(strip=True) for p in p_tags])
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





<

<br/>
<br/>

