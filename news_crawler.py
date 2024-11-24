import pandas as pd

from selenium import webdriver

import warnings
warnings.filterwarnings('ignore')

# 네이버 부동산 뉴스 - 우리동네 뉴스 서울특별시 행정구 코드
region_code_dic = {
        '강남구' : 1168000000
}


# 서울특별시 내 행정구 단위 부동산 뉴스 crawler 클래스
class NewsCrawler:

    def __init__(self, region_code) -> None:

        '''
            - chrome driver 멤버변수 초기화

            - args:
                - region_code: 행정구 code
        '''

        self.region_code = region_code

        self.driver = webdriver.Chrome()
        self.driver.get(f'https://land.naver.com/news/region.naver?city_no=1100000000&dvsn_no={self.region_code}')


    def get_basic_info(self) -> pd.DataFrame:

        '''
            - 각 페이지 내 뉴스 기사 기본 정보 get

            - args: None

            - return:
                - 본문 제외한 뉴스 기사 기본 정보 (한 페이지 단위)

        '''

        # idx, 기사 제목, 본문 링크, 작성일, 언론사
        idx_list, title_list, href_list, date_list, media_list = [], [], [], [], []
        for idx, tags in enumerate(self.driver.find_elements('xpath', '//ul[@class="headline_list live_list NEI=a:lst.title"]/li/dl')):
            
            a_tag_info = tags.find_element('xpath', './/dt[not(@class="photo")]/a')
            href = a_tag_info.get_attribute('href')
            title = a_tag_info.text

            media_info = tags.find_element('xpath', './/dd//span[@class="writing"]').text
            date_info = tags.find_element('xpath', './/dd//span[@class="date"]').text

            idx_list.append(idx+1)
            title_list.append(title)
            href_list.append(href)
            date_list.append(date_info)
            media_list.append(media_info)

        basic_news_info_dic = {
            'id' : idx_list,
            'title' : title_list,
            'link' : href_list,
            'date' : date_list,
            'media' : media_list
        }

        basic_news_info_dic['region_code'] = self.region_code

        return pd.DataFrame(basic_news_info_dic)


    def get_detail_article(self):

        '''
            - 뉴스 기사 본문
        '''

        pass

    
    def get_article_by_page(self):
        
        '''
            - link 끝 page num에 따라 뉴스 정보 get (상단 두 함수 for loop by page)
        '''

        pass


if __name__ == '__main__':

    region = region_code_dic['강남구']

    news_crawler = NewsCrawler(region_code=region)

    print(news_crawler.get_basic_info())