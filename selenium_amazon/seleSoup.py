from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from productPageExtract import getProductData
from primeVideoExtract import getPrimeVideoData
from handleCaptcha import handleCaptcha
from lxml import etree
import csv



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
        
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.set_page_load_timeout(TIMEOUT)
        self.wait = WebDriverWait(self.browser, TIMEOUT)

    def close(self):
        self.browser.close()

    def fetch(self, url):
        try:
            self.browser.get(url)
            return self.browser.page_source
        except TimeoutException:
            print("Timeout while fetching", url)
            return None
        
    def parse(self, asin, i):
        base_url = 'https://www.amazon.com/dp/'
        url = f'{base_url}{asin}/'
        content = self.fetch(url)
        if content:
            html = etree.HTML(content)
            title = html.xpath('normalize-space(//span[@id="productTitle"]/text())')
            if title:
                print(title)
                return getProductData(html, asin, i)
            else:
                title = html.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div[3]/div/div[2]/h1/text()')
                if title:
                    print(title)
                    return getPrimeVideoData(html, asin ,i)
                else:
                    handleCaptcha(self.browser)
                    return None
        else:
            return None

                
    def start_requests(self, i):
        # 构建CSV文件路径和保存文件路径
        csv_filename = f'../asin_seg_data/csv_{i}.csv'
        saved_filename = f'../crawled_seg_data/crawled_{i}.json'

        # 从CSV文件中读取一行数据并转换为列表
        with open(csv_filename, 'r', newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            row = next(csvreader)

        # 使用这个列表来生成start_ASINs列表
        start_ASINs = row

        max_retries = 3  # 最大重试次数
        retry_counts = {}  # 用于跟踪每个 asin 的重试次数

        while start_ASINs:
            asin = start_ASINs.pop(0)  # 从列表中获取一个 asin 进行处理

            # 尝试解析 asin 并获取 item
            item = self.parse(asin, i)  # 假设item是一个字典

            if item is None:
                # 如果 item 为 None，增加 asin 的重试次数
                retry_counts[asin] = retry_counts.get(asin, 0) + 1

                if retry_counts[asin] < max_retries:
                    # 将 asin 放回列表，以便重新处理
                    start_ASINs.append(asin)
                else:
                    # 达到最大重试次数，将链接标记为失效
                    print(f"Link for ASIN {asin} is marked as invalid after {max_retries} retries.")
            else:
                # 处理成功，将 item 存储到文件中
                with open(saved_filename, 'a', encoding='utf-8') as file:
                    json.dump(item, file, ensure_ascii=False, indent=4)  # 设置 indent 参数为 4，以缩进4个空格
                    file.write(',\n')  # 添加换行符，以便每个JSON对象都在单独的行上
                    
            
# if __name__ == "__main__":
#     crawler = AmazonCrawler()
#     crawler.start_requests(1)
#     crawler.close()

import multiprocessing

def run_crawler(i):
    crawler = AmazonCrawler()
    crawler.start_requests(i)
    crawler.close()

if __name__ == "__main__":
    # 创建四个进程，每个进程运行一个爬虫实例
    processes = []

    for i in range(1, 9):
        process = multiprocessing.Process(target=run_crawler, args=(i,))
        processes.append(process)

    # 启动进程
    for process in processes:
        process.start()

    # 等待所有进程完成
    for process in processes:
        process.join()

