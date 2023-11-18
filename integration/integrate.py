import json
import csv
import os

# 指定JSON文件所在的目录
directory_path = '../crawled_seg_data/'

# 创建CSV文件并写入标题行
csv_file = open('output.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)

# 写入CSV文件的标题行
header = ['ASIN', 'title', 'genre', 'version', 'score', 'run_time', 'release_date', 'starring_actors', 'supporting_actors']
csv_writer.writerow(header)

# 遍历指定目录下的所有文件
for filename in os.listdir(directory_path):
    if filename.endswith('.json'):
        with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

            # 遍历JSON数据并将每个条目写入CSV文件
            for item in data:
                asin = item.get('ASIN', '')
                title = item.get('title', '')
                genre = ', '.join(item.get('genre', []))
                version = item.get('version', '')
                score = item.get('score', '')
                run_time = item.get('run_time', '')
                release_date = item.get('release_date', '')
                starring_actors = item.get('starring_actors', '')
                supporting_actors = ', '.join(item.get('supporting_actors', ''))

                row = [asin, title, genre, version, score, run_time, release_date, starring_actors, supporting_actors]
                csv_writer.writerow(row)

# 关闭CSV文件
csv_file.close()

print("CSV文件已生成：output.csv")
