import re

PRODUCT_ERROR_ATTR_MSG = "产品界面解析错误"  # 查找基本属性产生的错误

def getProductData(html, asin, i):
    # 定义一个空字典来存储数据
    movie_data = {}

    try:
        movie_data["ASIN"] = asin
        # 电影名称
        movie_data["title"] = html.xpath('normalize-space(//span[@id="productTitle"]/text())')
        # 电影风格
        genre_list = []
        genre_list.extend([genre.strip() for genre in html.xpath('//a[@class="a-link-normal a-color-tertiary"][last()]/text()')])    # 类别
        genre_list.extend([genre.strip() for genre in html.xpath('//*[@id="productOverview_feature_div"]/div/table/tbody/tr[1]/td[2]/span/text()')]) # 流派
        movie_data["genre"] = genre_list
        # 电影版本
        movie_format = html.xpath('//div[@id="bylineInfo"]/span/text()')
        if len(movie_format) != 0:
            movie_data["version"] = movie_format[-1]
        # 电影贡献者表（contributers）
        contributers = html.xpath('//*[@id="productOverview_feature_div"]/div/table/tbody/tr[3]/td[2]/span[1]/span/span[2]/text()')
        # 电影评分
        movie_score = html.xpath('//span[@class="a-size-medium a-color-base"]/text()')
        if len(movie_score) != 0:
            movie_score = movie_score[0]
            movie_score = movie_score[0:movie_score.rfind('，')]
            movie_score = re.findall(r"\d+\.?\d*", movie_score)
            movie_data["score"] = movie_score[0]
        # 上映时间、电影时长
        movie_main_info = html.xpath('//span[@class="a-list-item"]//span/text()')# 电影主要信息
        for index in range(len(movie_main_info)):
            # 发布日期
            if "Release date" in movie_main_info[index]:
                movie_data["release_date"] = movie_main_info[index + 1].strip()
            # 运行时长
            if "Run time" in movie_main_info[index]:
                movie_data["run_time"] = movie_main_info[index + 1].strip()
            # 主演
            if "Actor" in movie_main_info[index] or "Actors" in movie_main_info[index]:
                starringActors = movie_main_info[index + 1].strip()
                # 从contributers 中去掉主演这一冗余信息
                contributers = [contributer for contributer in contributers if contributer.strip() not in starringActors]    # 去掉contributers中的director
                movie_data["starring_actors"] =  starringActors
            # 导演
            if "Director" in movie_main_info[index] or "Directors" in movie_main_info[index]:
                directors = movie_main_info[index + 1].strip()
                # 从contributers 中去掉导演这一冗余信息
                movie_data["directors"] = directors
                contributers = [contributer for contributer in contributers if contributer.strip() not in directors]    # 去掉contributers中的director
        # 剩下的是群众演员
        movie_data["supporting_actors"] = contributers
            

    except Exception as error:
        print(PRODUCT_ERROR_ATTR_MSG)
        print(f"ERROR FILE SEG{i}")

    # 返回一个字典
    return movie_data
