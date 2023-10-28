import json

class AmazonTestPipeline:
    def __init__(self):
        # 打开JSON文件以写入数据
        self.json_file = open('saved.json', 'w', encoding='utf-8')
        self.json_items = []

    def process_item(self, item, spider):
        try:
            # 在这里执行进一步的处理操作，例如将数据存储到JSON文件
            self.json_items.append(item)

        except Exception as e:
            # 处理异常情况
            spider.logger.error(f'Error processing item: {e}')

        return item

    def close_spider(self, spider):
        try:
            # 将数据写入JSON文件
            json.dump(self.json_items, self.json_file, ensure_ascii=False, indent=4)

        except Exception as e:
            # 处理异常情况
            spider.logger.error(f'Error writing JSON data: {e}')

        finally:
            # 关闭JSON文件
            self.json_file.close()
