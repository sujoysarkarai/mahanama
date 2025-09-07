import json
import os
import glob
import csv

def get_test_file_list(test_csv_file_path = '../../final_data/conll_format/list_of_possible_test_subchapters.csv'):
    # Initialize an empty list to store the file names
    file_names = []

    # Open and read the CSV file
    with open(test_csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            # Assuming each row is in the format: ['filename']
            # Strip the square brackets and single quotes
            cleaned_row = [item.strip("[]'") for item in row]
            # Extend the file_names list with the cleaned row
            file_names.extend(cleaned_row)

    return file_names


total_set = set()
correct_total = 0
correct_test = 0

file_paths = glob.glob(os.path.join('../../final_data/conll_format/v2/', '**/*.txt'), recursive=True)
file_paths_all = [os.path.basename(path) for path in file_paths]
file_paths_test = get_test_file_list()

with open('./test_file_with_clusters_split.jsonlines', 'r', encoding='utf-8') as f:
        lines = f.readlines()
for line in lines:
    data = json.loads(line)
    doc_key = os.path.basename(data["doc_key"])
    if doc_key in file_paths_test:
        correct_test += 1
    total_set.add(doc_key)
    
with open('./val_file_with_clusters_split.jsonlines', 'r', encoding='utf-8') as f:
        lines = f.readlines()
for line in lines:
    data = json.loads(line)
    doc_key = os.path.basename(data["doc_key"])
    total_set.add(doc_key)
    
with open('./train_file_with_clusters_split.jsonlines', 'r', encoding='utf-8') as f:
        lines = f.readlines()
for line in lines:
    data = json.loads(line)
    doc_key = os.path.basename(data["doc_key"])
    total_set.add(doc_key)

for path in total_set:
    if path in file_paths_all:
        correct_total += 1

print(len(total_set))
print(correct_total)
print(correct_test)