from selenium.webdriver.common.by import By
import re
from lxml import etree
from bs4 import BeautifulSoup
import json

PRIMEVIDEO_ERROR_ATTR_MSG = "PRIME VIDEO解析错误" 

def getPrimeVideoData(html, asin, i):
    # 定义一个空字典来存储数据
    movie_data = {}
    try:
        # 电影
        movie_data["ASIN"] = asin
        # 电影名称
        movie_data["title"] = html.xpath('//*[@id="main"]/div[1]/div/div/div[2]/div[3]/div/div[2]/h1/text()')

        script_element = html.xpath('//*[@id="main"]/script[9]')
        if len(script_element):
            script_json = json.loads(script_element[0].text)
            script_items = script_json['props']['state']['detail']['btfMoreDetails']
            script_items = list(script_items.values())
            script_item = script_items[0]
            if len(script_item):
                genres = script_item['genres']
                movie_genre = []
                for genre in genres:
                    movie_genre.append(genre['text'])
                movie_data["genre"] = movie_genre
                    
                # 电影版本
                movie_data["version"] = "Prime Video " + script_item['entityType']
                # 电影贡献者表（contributers）
                contributers = script_item['contributors']
                # 发布日期
                movie_data["release_date"] = script_item['releaseDate']
                # 运行时长
                movie_data['run_time'] = script_item['runtime']
                # 电影评分
                movie_data['rating'] = script_item['amazonRating']['value']

                # 提取主演信息
                starring_actors = []
                for actor in contributers['starringActors']:
                    starring_actors.append(actor['name'])

                # 提取导演信息
                directors = []
                for director in contributers['directors']:
                    directors.append(director['name'])

                # 提取群演信息
                supporting_actors = []
                for supporting_actor in contributers['supportingActors']:
                    supporting_actors.append(supporting_actor['name'])

                # 主演
                movie_data["starring_actors"] = starring_actors
                # 导演
                movie_data["directors"] = directors
                # 群演
                movie_data["supporting_actors"] =  supporting_actors
            
    except Exception:
        print(PRIMEVIDEO_ERROR_ATTR_MSG)
        print(f"ERROR FILE SEG{i}")

    # 返回一个字典
    return movie_data