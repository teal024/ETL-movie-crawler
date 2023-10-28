# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from logging import getLogger
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

class SeleniumMiddleware():
    def __init__(self, timeout=None):
        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument('--headless')
        # chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度

        # self.logger = getLogger(__name__)
        self.timeout = timeout
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)

    def __del__(self):
        self.browser.close()

    def process_request(self, request, spider):
        try:
            self.browser.get(request.url)
            # 在处理请求时将Selenium的driver实例存储在请求的meta中
            request.meta['driver'] = self.browser
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8',
                                status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(timeout=crawler.settings.get('SELENIUM_TIMEOUT'))


