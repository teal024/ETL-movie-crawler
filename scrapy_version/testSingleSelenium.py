import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from lxml import etree
import datetime
import re
import csv
from amazoncaptcha import AmazonCaptcha
import json

TIMEOUT = 30
USER_AGENT = 'Mozilla/5.0 (Linux; Android 7.0; SM-A520F Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/65.0.3325.109 Mobile Safari/537.36'
HEADERS = {
    'Host': 'www.amazon.com',
    'User-Agent': USER_AGENT,
}

class AmazonCrawler:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.set_page_load_timeout(TIMEOUT)
        self.wait = WebDriverWait(self.browser, TIMEOUT)


    def save_to_json(self, item):
        with open('saved.json', 'a', encoding='utf-8') as file:
            json.dump(item, file, ensure_ascii=False, indent=4)
            file.write(',\n')  # 添加逗号和换行符以便写入多个 JSON 对象
        

    def close(self):
        self.browser.close()

    def fetch(self, url):
        try:
            self.browser.get(url)
            return self.browser.page_source
        except TimeoutException:
            print("Timeout while fetching", url)
            return None
        

    def getData(self, html):
        # 电影名称
        movie_title = html.xpath('normalize-space(//span[@id="productTitle"]/text())')
        # 电影类型
        movie_category = html.xpath('//a[@class="a-link-normal a-color-tertiary"][last()]/text()')
        # 电影主演
        
        main_actor_list = []
        # 电影导演列表
        main_actor_list = []
        # 获取的所有演职员信息列表
        actor_director_info = html.xpath(
            '//span[@class="author notFaded"]/a[@class="a-link-normal"]/text()')

        more_actor_info = html.xpath('//span[@class="author"]/a[@class="a-link-normal"]/text()')
        actor_director_info = actor_director_info + more_actor_info

        # 获取到的所有演职员类型信息列表
        actor_director_category_info = html.xpath('//span[@class="contribution"]/span/text()')
        # 获取到的格式信息
        movie_format = html.xpath('//div[@id="bylineInfo"]/span/text()')
        if len(movie_format) != 0:
            movie_format = movie_format[-1]

        # 获取电影的评分
        movie_score = html.xpath('//span[@class="a-size-medium a-color-base"]/text()')
        if len(movie_score) != 0:
            movie_score = movie_score[0]
            movie_score = movie_score[0:movie_score.rfind('，')]
            movie_score = re.findall(r"\d+\.?\d*", movie_score)
            movie_score = movie_score[0]

        # 获取电影的评论总数
        movie_comment_num = html.xpath(
            '//a[@id="acrCustomerReviewLink"]//span[@class="a-size-base"]/text()')
        if len(movie_comment_num) != 0:
            movie_comment_num = re.findall(r"\d+\.?\d*", movie_comment_num[0])
            movie_comment_num = movie_comment_num[0]
        else:
            movie_comment_num = ""

        # 获取电影的near_asin
        movie_near_asin = html.xpath('//li[@class="swatchElement unselected"]//a/@href')
        movie_near_asin_list = []
        # 获取url中的asin信息
        for asin in movie_near_asin:
            near_asin_start_pos = asin.rfind('dp') + 3
            near_asin_end_pos = asin.rfind('ref')
            new_str = asin[near_asin_start_pos:near_asin_end_pos][-11:-1]
            movie_near_asin_list.append(new_str)

        # 电影版本
        movie_edition = html.xpath('//span[@id="editions"]/text()')

        director_list = set()
        # 处理演员信息和导演信息
        for index in range(len(actor_director_category_info)):
            if 'Actor' in actor_director_category_info[index]:
                main_actor_list.append(actor_director_info[index])
            if 'Director' in actor_director_category_info[index] or 'Author' in actor_director_category_info[index]:
                director_list.add(actor_director_info[index])

        # 电影主要信息
        movie_actor_list = ','.join(main_actor_list)
        movie_main_info = html.xpath('//span[@class="a-list-item"]//span/text()')

        movie_release_date = ""
        for index in range(len(movie_main_info)):
            # 获取发布日期
            if movie_main_info[index].strip()[0:4] == "发布日期":
                movie_release_date = movie_main_info[index + 1].strip()
            # 电影的演员列表
            if movie_main_info[index].strip()[0:2] == "演员":
                movie_actor_list = movie_main_info[index + 1]
                # print(movie_actor_list)
            if movie_main_info[index].strip()[0:2] == "导演":
                new_list = movie_main_info[index + 1].strip().split(',')

                for director in new_list:
                    director_list.add(director)
            if movie_main_info[index].strip()[0:4] == "ASIN":
                asin = movie_main_info[index + 1].strip()
            if movie_main_info[index].strip()[0:4] == "电影风格":
                movie_style = movie_main_info[index + 1].strip()


        current_time = datetime.datetime.now()
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        # 将提取的数据存储到一个字典中
        item = {
            "movie_title":movie_title,
            "movie_category":movie_category,
            "main_actor_list":main_actor_list,
            "actor_director_info":actor_director_info,
            "more_actor_info":more_actor_info,
            "movie_score":movie_score,
            "movie_comment_num":movie_comment_num,
            "movie_near_asin":movie_near_asin,
            "movie_edition":movie_edition,
            "movie_actor_list":movie_actor_list,
            "movie_main_info":movie_main_info,
            "movie_release_date":movie_release_date,
            "current_time": current_time_str,
        }

        return item
    

    def handleCaptcha(self, driver):
        try:
            self.total = driver.page_source
            soup = BeautifulSoup(self.total, features="lxml")
            # 找到验证码图片并解析
            src = soup.find(class_="a-row a-text-center").findChild(name="img").attrs["src"]
            captcha = AmazonCaptcha.fromlink(src)
            solution = captcha.solve(keep_logs=True)
            print(solution)
            # 输入验证码解决方案
            input_element = driver.find_element(By.ID, "captchacharacters")
            input_element.send_keys(solution)
            button = driver.find_element(By.XPATH, "//button")
            button.click()
            item = {
                "movie_title":"已解决验证码",
            }
            # print("已解决验证码√")
            # # 标记该ASIN为未处理，以便重新尝试
            # self.asinSet.iloc[self.index, 1] = False
        except:
            script_element = driver.find_element(By.XPATH, '//*[@id="main"]/script[9]')

            # 获取标签的内容
            script_content = script_element.get_attribute('innerHTML')

            # 由于内容是字符串，我们需要使用 json.loads 将其解析为 JSON
            json_data = json.loads(script_content)
            item = dict(json_data)
            item = {
                "movie_title":"另一种情况",
            }
        
        return item

    def parse(self, url):
        content = self.fetch(url)
        if content:
            html = etree.HTML(content)
            title = html.xpath('//span[@id="productTitle"]/text()')
            if title:
                return self.getData(html)
            else:
                return self.handleCaptcha(self.browser)


    def start_requests(self):
        start_urls = [      #
            'https://www.amazon.com/dp/B00006HAXW/',
            'https://www.amazon.com/dp/B003AI2VGA/',
            'https://www.amazon.com/dp/B00004CQT3/',
            'https://www.amazon.com/dp/B00004CQT4/',
            'https://www.amazon.com/dp/B0078V2LCY/',
            'https://www.amazon.com/dp/B003ZG3GAM/',
            'https://www.amazon.com/dp/B004BH1TN0/',
        ]
        for url in start_urls:
            item = self.parse(url)
            self.save_to_json(item)
            print(item)  # You can do something with the item here.


if __name__ == "__main__":
    crawler = AmazonCrawler()
    crawler.start_requests()
    crawler.close()



