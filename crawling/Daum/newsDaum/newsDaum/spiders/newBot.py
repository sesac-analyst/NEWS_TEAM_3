
import scrapy
import json
import requests
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from user_agent import generate_user_agent

headers = {'User-Agent': generate_user_agent(os='mac', device_type='desktop')}

class DaumStockSpider(scrapy.Spider):
    name = "daum_stock"
    
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumStockSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/estate?page={}&regDate={}'
        self.start_date = date(2024, 8, 31)
        self.end_date = self.start_date - relativedelta(months=1)
        self.current_page = 1
        self.previous_page_content = None

    def start_requests(self):
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            if self.start_date > self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
                url = self.base_url.format(self.current_page, date_str)
                yield scrapy.Request(url=url, callback=self.parse, headers=headers)
            return
        else:
            self.previous_page_content = current_page_content

        detail_urls = response.xpath('//*[@id="mArticle"]/div[3]/ul/li/div/strong/a/@href').getall()
        for detail_url in detail_urls:
            try:
                yield scrapy.Request(url=detail_url, callback=self.parse_article, headers=headers)
            except Exception as e:
                self.logger.error(f"Error while requesting detail page: {e}")
                continue

        self.current_page += 1
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    def parse_article(self, response):
        current_url = response.url
        article_id = current_url.split("/")[-1]
        s_header = {
            "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "referer": current_url,
            "Accept": 'application/json, text/plain, */*',
            "Accept-encoding": 'gzip, deflate, br, zstd',
            "Accept-language": 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://v.daum.net',
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiMzQyNGZjZS05ZDRiLTQwNWEtYjZhZS0wMDJhYmQ4NjViZDQiLCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgiLCJmb3J1bV9rZXkiOiJuZXdzIiwiZm9ydW1faWQiOi05OSwiZ3JhbnRfdHlwZSI6ImFsZXhfY3JlZGVudGlhbHMiLCJhdXRob3JpdGllcyI6WyJST0xFX0NMSUVOVCJdLCJzY29wZSI6W10sImV4cCI6MTcyNTg2MTI1M30.8Ru-_tHEsAzPeLKoczyGZ_URstmjlq0xIC5qbNVGLdQ"
        }
        
        # 스티커 데이터를 가져오기 위한 API URL 수정
        sticker_api_url = f"https://action.daum.net/apis/v1/reactions/home?itemKey={article_id}"
        
        try:
            res = requests.get(url=sticker_api_url, headers=s_header)
            res.raise_for_status()
            sticker_data = json.loads(res.content)['item']['stats']

            # 스티커 데이터 처리
            stickers = [
                {'name': '추천해요', 'count': sticker_data.get("RECOMMEND", 0)},
                {'name': '좋아요', 'count': sticker_data.get("LIKE", 0)},
                {'name': '감동이에요', 'count': sticker_data.get("IMPRESS", 0)},
                {'name': '화나요', 'count': sticker_data.get("ANGRY", 0)},
                {'name': '슬퍼요', 'count': sticker_data.get("SAD", 0)},
            ]
        except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to retrieve or parse sticker data: {e}")
            stickers = [{'name': '', 'count': 0} for _ in range(5)]

        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        editor = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        publication_date = "".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        publisher = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        content = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])

        yield {
            'platform': '다음',
            'category': '부동산',
            'publisher': publisher,
            'publication_date': date,
            'title': title,
            'content': content,
            'editor': editor,
            'article_url': current_url,
            'stk1_name': stickers[0]['name'],
            'stk1_count': stickers[0]['count'],
            'stk2_name': stickers[1]['name'],
            'stk2_count': stickers[1]['count'],
            'stk3_name': stickers[2]['name'],
            'stk3_count': stickers[2]['count'],
            'stk4_name': stickers[3]['name'],
            'stk4_count': stickers[3]['count'],
            'stk5_name': stickers[4]['name'],
            'stk5_count': stickers[4]['count'],
        }



# class DaumNewsSpider(scrapy.Spider):
#     name = 'news_daum_v1'
#     subcategories = {
#         "economic/finance": "금융",
#         "economic/industry": "산업",
#         "economic/employ": "취업_고용",
#         "economic/autos": "자동차",
#         "economic/stock": "주식",
#         "economic/estate": "부동산",
#         "economic/consumer": "소비자",
#         "economic/worldeconomy": "국제경제",
#         "economic/coin": "가상자산",
#         "economic/pension": "연금_노후",
#         "economic/policy": "경제정책",
#         "economic/startup": "벤처_스타트업"
#     }


# import json
# import scrapy
# import requests
# from datetime import date, timedelta
# from dateutil.relativedelta import relativedelta
# from user_agent import generate_user_agent

# headers = {'User-Agent': generate_user_agent(os='mac', device_type='desktop')}

# class DaumStockSpider(scrapy.Spider):
#     name = "daum_stock"
    
#     handle_httpstatus_list = [301, 302]

#     def __init__(self, *args, **kwargs):
#         super(DaumStockSpider, self).__init__(*args, **kwargs)
#         self.base_url = 'https://news.daum.net/breakingnews/economic/autos?page={}&regDate={}'
#         self.start_date = date(2024, 8, 31)
#         self.end_date = self.start_date - relativedelta(months=1)
#         self.current_page = 1
#         self.previous_page_content = None

#     def start_requests(self):
#         date_str = self.start_date.strftime('%Y%m%d')
#         url = self.base_url.format(self.current_page, date_str)
#         yield scrapy.Request(url=url, callback=self.parse, headers=headers)

#     def parse(self, response):
#         current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        
#         if current_page_content == self.previous_page_content:
#             self.start_date -= timedelta(days=1)
#             if self.start_date > self.end_date:
#                 self.current_page = 1
#                 date_str = self.start_date.strftime('%Y%m%d')
#                 url = self.base_url.format(self.current_page, date_str)
#                 yield scrapy.Request(url=url, callback=self.parse, headers=headers)
#             return
#         else:
#             self.previous_page_content = current_page_content

#         detail_urls = response.xpath('//*[@id="mArticle"]/div[3]/ul/li/div/strong/a/@href').getall()
#         for detail_url in detail_urls:
#             try:
#                 yield scrapy.Request(url=detail_url, callback=self.parse_article, headers=headers)
#             except Exception as e:
#                 self.logger.error(f"Error while requesting detail page: {e}")
#                 continue

#         self.current_page += 1
#         date_str = self.start_date.strftime('%Y%m%d')
#         next_url = self.base_url.format(self.current_page, date_str)
#         yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

#     def parse_article(self, response):
#         current_url = response.url
#         article_id = current_url.split("/")[-1]
#         s_header = {"User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
#             "referer": current_url,
#             "Accept" : 'application/json, text/plain, */*',
#             "Accept-encoding" : 'gzip, deflate, br, zstd',
#             "Accept-language" : 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
#             'Origin' : 'https://v.daum.net',
#             "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJiMzQyNGZjZS05ZDRiLTQwNWEtYjZhZS0wMDJhYmQ4NjViZDQiLCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgiLCJmb3J1bV9rZXkiOiJuZXdzIiwiZm9ydW1faWQiOi05OSwiZ3JhbnRfdHlwZSI6ImFsZXhfY3JlZGVudGlhbHMiLCJhdXRob3JpdGllcyI6WyJST0xFX0NMSUVOVCJdLCJzY29wZSI6W10sImV4cCI6MTcyNTg2MTI1M30.8Ru-_tHEsAzPeLKoczyGZ_URstmjlq0xIC5qbNVGLdQ"
#             }
        
#         # 스티커 데이터를 가져오기 위한 API URL 수정
#         sticker_api_url = f"https://action.daum.net/apis/v1/reactions/home?itemKey={article_id}"
        
#         try:
#             res = requests.get(url=sticker_api_url, headers=s_header)
#             res.raise_for_status()
#             sticker_data = json.loads(res.content)['item']['stats']

#             # 스티커 데이터 처리
#             sticker = {
#                 "LIKE": sticker_data.get("LIKE", 0),
#                 "SAD": sticker_data.get("SAD", 0),
#                 "ANGRY": sticker_data.get("ANGRY", 0),
#                 "RECOMMEND": sticker_data.get("RECOMMEND", 0),
#                 "IMPRESS": sticker_data.get("IMPRESS", 0),
#             }
#         except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
#             self.logger.error(f"Failed to retrieve or parse sticker data: {e}")
#             sticker = {}

#         title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
#         editor = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
#         date = response.css('.num_date::text').get()
#         publication_date = "".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
#         publisher = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
#         content = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])

#         yield {
#             'platform': '다음',
#             'category': '자동차',
#             'publisher': publisher,
#             'publication_date': date,
#             'title': title,
#             'content': content,
#             'editor': editor,
#             'article_url': current_url,
#             'sticker': sticker
#         }




class DaumIndustrySpider(scrapy.Spider):
    name = "daum_industry"
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumIndustrySpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic/finance?page={}&regDate={}'
        self.start_date = date(2024, 9, 3)
        self.end_date = self.start_date - relativedelta(days=8)
        self.current_page = 1
        self.previous_page_content = None

    def start_requests(self):
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            if self.start_date > self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
                url = self.base_url.format(self.current_page, date_str)
                yield scrapy.Request(url=url, callback=self.parse, headers=headers)
            return
        else:
            self.previous_page_content = current_page_content

        detail_urls = response.xpath('//*[@id="mArticle"]/div[3]/ul/li/div/strong/a/@href').getall()
        for detail_url in detail_urls:
            try:
                yield scrapy.Request(url=detail_url, callback=self.parse_article, headers=headers)
            except Exception as e:
                self.logger.error(f"Error while requesting detail page: {e}")
                continue

        self.current_page += 1
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    def parse_article(self, response):
        current_url = response.url
        article_id = current_url.split("/")[-1]
        s_header = {"User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "referer": current_url,
            "Accept" : 'application/json, text/plain, */*',
            "Accept-encoding" : 'gzip, deflate, br, zstd',
            "Accept-language" : 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6',
            'Origin' : 'https://v.daum.net',
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxMzJhNWRiYS1kZGY1LTRiYzAtOGM4YS1jMmYyMzk1ODkxZDIiLCJjbGllbnRfaWQiOiIyNkJYQXZLbnk1V0Y1WjA5bHI1azc3WTgiLCJmb3J1bV9rZXkiOiJuZXdzIiwiZm9ydW1faWQiOi05OSwiZ3JhbnRfdHlwZSI6ImFsZXhfY3JlZGVudGlhbHMiLCJhdXRob3JpdGllcyI6WyJST0xFX0NMSUVOVCJdLCJzY29wZSI6W10sImV4cCI6MTcyNTUxNzY1MH0.yoaU0EGLL2RvO5CKT1QyHu0NJM5Y0talJETZGHZT5pM"
            }
        
        # 스티커 데이터를 가져오기 위한 API URL 수정
        sticker_api_url = f"https://action.daum.net/apis/v1/reactions/home?itemKey={article_id}"
        
        try:
            res = requests.get(url=sticker_api_url, headers=s_header)
            res.raise_for_status()
            sticker_data = json.loads(res.content)['item']['stats']

            # 스티커 데이터 처리
            sticker = {
                "LIKE": sticker_data.get("LIKE", 0),
                "SAD": sticker_data.get("SAD", 0),
                "ANGRY": sticker_data.get("ANGRY", 0),
                "RECOMMEND": sticker_data.get("RECOMMEND", 0),
                "IMPRESS": sticker_data.get("IMPRESS", 0),
            }
        except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to retrieve or parse sticker data: {e}")
            sticker = {}

        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        editor = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        date = response.css('.num_date::text').get()
        publication_date = "".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        publisher = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        content = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])

        yield {
            'platform': '다음',
            'category': '산업',
            'publisher': publisher,
            'publication_date': date,
            'title': title,
            'content': content,
            'editor': editor,
            'article_url': current_url,
            'sticker': sticker
        }

    






# class DaumAllSpider(scrapy.Spider):
    name = "daum_all"
    handle_httpstatus_list = [301, 302]

    def __init__(self, *args, **kwargs):
        super(DaumAllSpider, self).__init__(*args, **kwargs)
        self.base_url = 'https://news.daum.net/breakingnews/economic?page={}&regDate={}'
        self.start_date = date(2024, 8, 31)
        self.end_date = self.start_date - relativedelta(days=1)
        self.current_page = 1
        self.previous_page_content = None

    def start_requests(self):
        date_str = self.start_date.strftime('%Y%m%d')
        url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=url, callback=self.parse, headers=headers)

    def parse(self, response):
        current_page_content = ''.join(response.css('.box_etc > ul > li > div > strong > a::text').getall())
        
        if current_page_content == self.previous_page_content:
            self.start_date -= timedelta(days=1)
            if self.start_date > self.end_date:
                self.current_page = 1
                date_str = self.start_date.strftime('%Y%m%d')
                url = self.base_url.format(self.current_page, date_str)
                yield scrapy.Request(url=url, callback=self.parse, headers=headers)
            return
        else:
            self.previous_page_content = current_page_content

        detail_urls = response.xpath('//*[@id="mArticle"]/div[3]/ul/li/div/strong/a/@href').getall()
        for detail_url in detail_urls:
            try:
                yield scrapy.Request(url=detail_url, callback=self.parse_article, headers=headers)
            except Exception as e:
                self.logger.error(f"Error while requesting detail page: {e}")
                continue

        self.current_page += 1
        date_str = self.start_date.strftime('%Y%m%d')
        next_url = self.base_url.format(self.current_page, date_str)
        yield scrapy.Request(url=next_url, callback=self.parse, headers=headers)

    def parse_article(self, response):
        current_url = response.url
        article_id = current_url.split("/")[-1]
        s_header = {
            "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "referer": current_url
        }

        try:
            res = requests.get(url=f"https://v.daum.net/v/{article_id}", headers=s_header)
            res.raise_for_status()
            sticker_data = json.loads(res.text)
            sticker = {key: value for key, value in sticker_data["item"]["stats"].items() if key in ["LIKE", "SAD", "ANGRY", "RECOMMEND", "IMPRESS"]}
        except (requests.exceptions.RequestException, KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to retrieve or parse sticker data: {e}")
            sticker = {}
        title = response.xpath('//*[@id="mArticle"]/div[1]/h3/text()').get()
        editor = "".join([text for text in response.css('.txt_info::text').getall() if text not in ["입력 ", "수정 ", "개"]])
        
        date = response.css('.num_date::text').get()
        publication_date = "".join([c_date for c_date in response.css(".num_date::text").getall() if c_date != date])
        publisher = response.xpath('//*[@id="kakaoServiceLogo"]/text()').get()
        content = " ".join([sent.strip() for sent in response.xpath('//*[@id="mArticle"]/div[2]/div/section/p/text()').getall()])

        yield {
            'platform' : '다음',
            'category' : '산업',
            'publisher': publisher,
            'publication_date': date,
            'title': title,
            'content': content,
            'editor': editor,
            'article_url': current_url
            # 'sticker': sticker
        }









