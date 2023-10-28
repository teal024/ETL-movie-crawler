import scrapy
import json
from scrapy.selector import Selector
from lxml import etree
import datetime
import re
from bs4 import BeautifulSoup
from amazoncaptcha import AmazonCaptcha
from selenium.webdriver.common.by import By

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['amazon.com']
    page = 1
    lost_item = 0
    rh = 'n%3A11091801'
    cookies = {
        "anonymid": "j7wsz80ibwp8x3",
        "_r01_": "1",
        "ln_uact": "mr_mao_hacker@163.com",
        "_de": "BF09EE3A28DED52E6B65F6A4705D973F1383380866D39FF5",
        "depovince": "GW",
        "jebecookies": "2fb888d1-e16c-4e95-9e59-66e4a6ce1eae|||||",
        "ick_login": "1c2c11f1-50ce-4f8c-83ef-c1e03ae47add",
        "p": "158304820d08f48402be01f0545f406d9",
        "first_login_flag": "1",
        "ln_hurl": "http://hdn.xnimg.cn/photos/hdn521/20180711/2125/main_SDYi_ae9c0000bf9e1986.jpg",
        "t": "adb2270257904fff59f082494aa7f27b9",
        "societyguester": "adb2270257904fff59f082494aa7f27b9",
        "id": "327550029",
        "xnsid": "4a536121",
        "loginfrom": "syshome",
        "wp_fold": "0"
    }

    headers = {
        'Host': 'www.amazon.com',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; \
                        SM-A520F Build/NRD90M; wv) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Version/4.0 \
                        Chrome/65.0.3325.109 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,\
                        application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    def start_requests(self):
        """
            start_requests做为程序的入口，可以重写，自定义第一批请求
            可以添加headers、cookies, , dont_filter=True
        """
        start_urls = [
            'https://www.amazon.com/dp/B00006HAXW/',
            'https://www.amazon.com/dp/B003AI2VGA/',
            'https://www.amazon.com/dp/B00004CQT3/',
            'https://www.amazon.com/dp/B00004CQT4/',
            'https://www.amazon.com/dp/B0078V2LCY/',
            'https://www.amazon.com/dp/B003ZG3GAM/',
            'https://www.amazon.com/dp/B004BH1TN0/',
        ]

        for url in start_urls:
            yield scrapy.Request(url=url, headers=self.headers,
                              callback=self.parse)

    def getData(self, html):
        # 提取title
        movie_title = html.xpath('normalize-space(//span[@id="productTitle"]/text())')
        # 提取电影类型
        movie_category = html.xpath('//a[@class="a-link-normal a-color-tertiary"][last()]/text()')
        # 电影主演列表
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


    def parse(self, response):
        driver = response.meta['driver']
        # 获取页面内容
        page_content = response.text
        html = etree.HTML(page_content)

        title = html.xpath('//span[@id="productTitle"]/text()')
        if title:
            item = self.getData(html)
        else:
            item = self.handleCaptcha(driver)

        yield item

            