import csv

f = open('movies.txt', 'rb')
movies_list = []
batch_size = 4000
current_batch = 0
csv_file_counter = 1
csv_filename = f'csv_{csv_file_counter}.csv'
csv_writer = csv.writer(open(csv_filename, 'w', newline=''))

while True:
    line = f.readline()
    if not line:
        break
    else:
        try:
            line_gbk = line.decode('gbk', 'ignore')
        except Exception as e:
            print(e)
        
        if 'product/productId' in line_gbk:
            asin = line_gbk.split('product/productId: ')[-1].strip('\n')
            if asin not in movies_list:
                movies_list.append(asin)
                current_batch += 1
                if current_batch == batch_size:
                    # Write the current batch of ASINs to the CSV file
                    csv_writer.writerow(movies_list)
                    movies_list = []  # Clear the list for the next batch
                    current_batch = 0
                    csv_file_counter += 1
                    csv_filename = f'csv_{csv_file_counter}.csv'
                    csv_writer = csv.writer(open(csv_filename, 'w', newline=''))

# Write any remaining ASINs to the last CSV file
if movies_list:
    csv_writer.writerow(movies_list)

# Close the input file
f.close()
