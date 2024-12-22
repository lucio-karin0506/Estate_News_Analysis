import pandas as pd
import numpy as np

import requests
from selenium import webdriver
from bs4 import BeautifulSoup

from tqdm.auto import tqdm

import warnings
warnings.filterwarnings('ignore')

# 네이버 부동산 뉴스 - 우리동네 뉴스 서울특별시 행정구 코드
region_code_dic = {
        # '강남구' : 1168000000,
        # '강동구' : 1174000000
        # '강북구' : 1130500000,
        # '강서구' : 1150000000,  
        # '관악구' : 1162000000,
        # '광진구' : 1121500000,
        # '구로구' : 1153000000,
        # '금천구' : 1154500000,
        '노원구' : 1135000000,
        '도봉구' : 1132000000,
        '동대문구' : 1123000000,
        '동작구' : 1159000000,
        '마포구' : 1144000000,
        '서대문구' : 1141000000,
        '서초구' : 1165000000,
        '성동구' : 1120000000,
        '성북구' : 1129000000,
        '송파구' : 1171000000,
        '양천구' : 1147000000,
        '영등포구' : 1156000000,
        '용산구' : 1117000000,
        '은평구' : 1138000000,
        '종로구' : 1111000000,
        '중구' : 1114000000,
        '중랑구' : 1126000000,
}


# 서울특별시 내 행정구 단위 부동산 뉴스 crawler 클래스
class NewsCrawler:

    def __init__(self, region_code: int, page_num: int) -> None:

        '''
            - chrome driver & 지역코드 멤버변수 초기화

            - args:
                - region_code: 행정구 code

            - return: None
        '''

        self.region_code = region_code
        self.page_num = page_num

        self.driver = webdriver.Chrome()
        self.driver.get(f'https://land.naver.com/news/region.naver?city_no=1100000000&dvsn_no={self.region_code}&page={self.page_num}')


    def get_detail_article(self, news_url: str) -> str:

        '''
            - 각 페이지 내 뉴스 기사 본문 크롤링

            - args:
                - news_url: 뉴스 기사 url

            - return:
                - article_text: 뉴스 기사 본문
        '''

        # HTTP GET 요청
        response = requests.get(news_url)

        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        article_tag = soup.select_one('#dic_area')

        try:
            article_text = article_tag.get_text(separator='', strip=True)
            return article_text
        
        except:
            return np.nan


    def get_basic_info(self) -> pd.DataFrame:

        '''
            - 각 페이지 내 뉴스 기사 기본 정보 get

            - args: None

            - return:
                - 본문 제외한 뉴스 기사 기본 정보 (한 페이지 단위)

        '''

        # idx, 기사 제목, 본문 링크, 작성일, 언론사
        title_list, href_list, article_list, date_list, media_list = [], [], [], [], []
        for _, tags in enumerate(self.driver.find_elements('xpath', '//ul[@class="headline_list live_list NEI=a:lst.title"]/li/dl')):
            
            a_tag_info = tags.find_element('xpath', './/dt[not(@class="photo")]/a')
            href = a_tag_info.get_attribute('href')
            title = a_tag_info.text

            article = self.get_detail_article(href)

            media_info = tags.find_element('xpath', './/dd//span[@class="writing"]').text
            date_info = tags.find_element('xpath', './/dd//span[@class="date"]').text

            title_list.append(title)
            href_list.append(href)
            article_list.append(article)
            date_list.append(date_info)
            media_list.append(media_info)

        basic_news_info_dic = {
            'title' : title_list,
            'link' : href_list,
            'article' : article_list,
            'date' : date_list,
            'media' : media_list
        }

        basic_news_info_dic['region_code'] = self.region_code

        return pd.DataFrame(basic_news_info_dic)
    

    def get_page_num(self) -> int:

        '''
            - 페이지 수 탐색
        '''
        page_num = self.driver.find_element('xpath', '//*[@id="content"]/div[3]/a[strong]/strong').text

        return int(page_num)


if __name__ == '__main__':

    for region, region_code in region_code_dic.items():

        print(region)

        news_result_df_list = []
        for page_num in tqdm(range(1, 140), leave=True): # page range 1 ~ 135는 2010년 6월까지 가장 많은 페이지를 갖는 중구 기준

            news_crawler = NewsCrawler(region_code=region_code, page_num=page_num)

            real_page_num = news_crawler.get_page_num()

            if real_page_num == page_num:
                news_result_df = news_crawler.get_basic_info()
                news_result_df_list.append(news_result_df)

            else:
                break

        final_news_result_df = pd.concat(news_result_df_list, ignore_index=True).drop_duplicates()
        final_news_result_df['region'] = region
        final_news_result_df.to_csv(f'{region}_news.csv', encoding='utf-8-sig')