import re
import json
import glob
import os
import random
from tqdm import tqdm
import csv
import pandas as pd

def get_head_dict(exl_file_path= '../../final_data/cluster_data_for_manual_verification_df_apply_correction.xlsx'):
    # Read the Excel file
    df = pd.read_excel(exl_file_path)
    # Create the dictionary
    cluster_dict = dict(zip(df['cluster_head_id'], df['cluster_head_name']))
    return cluster_dict

def get_doc_key(lines):
    json_lines = [json.loads(line) for line in lines]
    doc_key_lines = [line["doc_key"] for line in json_lines]
    return doc_key_lines

def get_test_file_list_all(test_csv_file_path= '../../final_data/conll_format/list_of_possible_test_subchapters.csv'):
    # Initialize an empty list to store the file names
    file_names_test = []

    # Open and read the CSV file
    with open(test_csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            # Assuming each row is in the format: ['filename']
            # Strip the square brackets and single quotes
            cleaned_row = [item.strip("[]'") for item in row]
            # Extend the file_names list with the cleaned row
            file_names_test.extend(cleaned_row)

    folder_path = '../../final_data/conll_format/v2/'
    file_paths = glob.glob(os.path.join(folder_path, '**/*.txt'), recursive=True)
    file_paths_fillered = []

    for file_path in file_paths:
        if os.path.basename(file_path) in file_names_test:
            file_paths_fillered.append(file_path)

    return file_paths_fillered

def get_test_file_list_form_split(test_split_file_path= './test_file_with_clusters_split.jsonlines'):
    
    with open(test_split_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    doc_names = get_doc_key(lines)

    with open('test_file_list.txt', 'w', encoding='utf-8') as f:
        for line in doc_names:
            f.write(line)
            f.write('\n')
    return doc_names

def get_test_file_list_form_txt(test_txt_file_path= './test_file_list.txt'):
    
    with open(test_txt_file_path, 'r', encoding='utf-8') as f:
        doc_names = [line.strip() for line in f.readlines()]
    return doc_names

def split_jsonlines(file_path, base_dir, test_list, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    # Ensure the ratios add up to 1.0
    assert train_ratio + val_ratio + test_ratio == 1.0, "Ratios must add up to 1.0"

    # Read the JSON lines file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Shuffle the lines randomly
    random.shuffle(lines)

    # Calculate the number of lines for each split
    total_lines = len(lines)
    test_count = int(total_lines * test_ratio)

    test_curr_count = 0
    test_lines = []
    remaining_lines = []

    # Ensure all the test files are selected from the test_list
    for line in tqdm(lines):
        json_line = json.loads(line)
        # Extract the file name from the doc_key
        file_name = os.path.basename(json_line["doc_key"])
        if test_curr_count < test_count and file_name in test_list:
            test_lines.append(line)
            test_curr_count += 1
        else:
            remaining_lines.append(line)
    
    # Ensure remaining lines are also shuffled
    random.shuffle(remaining_lines)

    # Calculate the number of lines for train and val splits from remaining lines
    remaining_lines_count = len(remaining_lines)
    train_count = int(remaining_lines_count * (train_ratio / (train_ratio + val_ratio)))
    val_count = remaining_lines_count - train_count  # Ensuring no loss due to rounding

    # Split the remaining lines
    train_lines = remaining_lines[:train_count]
    val_lines = remaining_lines[train_count:]

    # Write the splits to separate files
    # base_dir = './litbank_data3/' # os.path.dirname(file_path)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    train_file = os.path.join(base_dir, 'train_file_with_clusters_split.jsonlines')
    val_file = os.path.join(base_dir, 'val_file_with_clusters_split.jsonlines')
    test_file = os.path.join(base_dir, 'test_file_with_clusters_split.jsonlines')
    test_file_without_clusters = os.path.join(base_dir, 'test_file_without_clusters_split.jsonlines')


    with open(train_file, 'w', encoding='utf-8') as f:
        for line in train_lines:
            f.write(line)
    
    with open(val_file, 'w', encoding='utf-8') as f:
        for line in val_lines:
            f.write(line)
    
    with open(test_file, 'w', encoding='utf-8') as f:
        for line in test_lines:
            f.write(line)

     # Create test_file_without_clusters
    with open(test_file_without_clusters, 'w', encoding='utf-8') as f:
        for line in test_lines:
            json_line = json.loads(line)
            json_line_without_clusters = {
                "doc_key": json_line["doc_key"],
                "tokens": json_line["tokens"]
            }
            f.write(json.dumps(json_line_without_clusters) + '\n')

    print(f"Data split complete. Files saved to: \n{train_file}\n{val_file}\n{test_file}\n{test_file_without_clusters}")
    print(f"Data split, train - {len(train_lines)}, val - {len(val_lines)}, test - {len(test_lines)}")


def split_document(doc, max_tokens=1024):
    """
    Splits a document into multiple smaller documents if it exceeds max_tokens.
    Adjusts the clusters accordingly.
    """
    tokens = doc['tokens']
    clusters = doc['clusters']
    clusters_strings = doc['clusters_strings']
    doc_key = doc['doc_key']
    
    # List to hold split documents
    split_docs = []
    # print(clusters)
    
    # Split tokens into chunks of size max_tokens
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_clusters = []
        chunk_clusters_strings = []
        valid = False
        head_word_to_entity_number = dict() 
        
        # Adjust clusters for the current chunk
        for cluster, cluster_strings in zip(clusters, clusters_strings):
            new_cluster = []
            new_cluster_strings = []
            for position, position_String in zip(cluster, cluster_strings):
                start, end = position
                # Check if cluster falls within the current chunk
                if end <= i:
                    continue
                if start >= i + max_tokens:
                    break
                    
                new_cluster.append([start - i , end - i])
                new_cluster_strings.append(position_String)
                
            if new_cluster:
                chunk_clusters.append(new_cluster)
                chunk_clusters_strings.append(new_cluster_strings)
        
        # Create a new document for the current chunk
        split_doc = {
            "doc_key": f"{doc_key}_part_{len(split_docs)}",
            "tokens": chunk_tokens,
            "clusters": chunk_clusters,
            "clusters_strings": chunk_clusters_strings
        }
        split_docs.append(split_doc)
    
    return split_docs



def conll_to_json(conll_file, head_dict):
    token_number = 0
    valid = False
    head_word_to_entity_number = dict() 

    with open(conll_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        parts = line.split('\t')
        if len(parts) >= 3:

            # Check for clustering annotations
            if len(parts) > 3:
                entities = parts[3].split("|")
                head_names = parts[4].split("|")
                for entity, head_name in zip(entities, head_names):
                    entity_number = str(entity.replace('(','').replace(')',''))
                    head_name = head_dict[entity_number] # str(head_name.replace('(','').replace(')',''))
                    # head_name = parts[2]
                    if head_word_to_entity_number.get(head_name) is None:  # 1st time
                        head_word_to_entity_number[head_name] = dict()
                    if head_word_to_entity_number.get(head_name).get(entity_number) is None:  # 1st time
                        head_word_to_entity_number[head_name][entity_number] = []
                    head_word_to_entity_number[head_name][entity_number].append([token_number, token_number])

            token_number += 1

    list_homoname_clusters = [] 
    list_homoname_heads = [] 
    list_keys = []
    for head_name in head_word_to_entity_number.keys():
        if len(head_word_to_entity_number[head_name].keys()) == 1:
            continue
        valid = True
        list_homoname_cluster = []
        list_key = []
        for key, value in head_word_to_entity_number[head_name].items():
            list_homoname_cluster.append(value)
            list_key.append(key)
        list_homoname_clusters.append(list_homoname_cluster)
        list_homoname_heads.append(head_name)
        list_keys.append(list_key)

    return list_homoname_clusters, valid, list_homoname_heads, list_keys

def print_homo(selected_files, jsonl_output, homoname_heads, idx = 17):
    print(selected_files[idx])
    print(jsonl_output[idx])
    print(homoname_heads[idx])

def jsonlines_construct(file_paths, head_dict, max_tokens = 1024):
    
    jsonl_output = []
    selected_files = []
    homoname_heads = []
    keys = []
    for file_path in tqdm(file_paths):
        json_output, is_vaild, homoname_head, key = conll_to_json(file_path, head_dict)
        if is_vaild:
            selected_files.append(file_path)
            jsonl_output.append(json_output)
            keys.append(key)
            homoname_heads.append(homoname_head)

    print(len(jsonl_output))
    # print_homo(selected_files, jsonl_output, homoname_heads, 5)
    
    # split_documents_jsonl_output = []
    
    # for doc in jsonl_output:
    #     doc_len = len(doc['tokens']) # + 4 * len([clu for clu in doc['clusters']]) + len(doc['doc_key'])
        
    #     if doc_len >= max_tokens:
    #         print(doc_len)
    #         split_docs = split_document(doc, max_tokens)
    #         split_documents_jsonl_output.extend(split_docs)
    #     else:
    #         split_documents_jsonl_output.append(doc)

    # print(len(split_documents_jsonl_output))
    # return split_documents_jsonl_output

    return jsonl_output, selected_files, homoname_heads, keys

def read_jsonlines(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    homoname_dict = {}
    for line in lines:
        data = json.loads(line)
        doc_key = data["doc_key"]
        cluster_head = data["cluster_head"]
        clusters = data["clusters"]
        
        homoname_dict[doc_key] = (cluster_head, clusters)
    
    return homoname_dict

def write_jsonlines(jsonl_file_path, selected_files, homoname_heads, jsonl_output, keys):
    # Ensure the output directory exists
    output_directory = jsonl_file_path
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Writing to a JSON lines file
    output_jsonl_file = os.path.join(output_directory, 'homonames_file_with_clusters.jsonlines')
    with open(output_jsonl_file, 'w', encoding='utf-8') as f:
        for idx in range(len(jsonl_output)):
            output = {
                "doc_key": selected_files[idx],
                "cluster_head": homoname_heads[idx],
                "cluster_entity_numbers": keys[idx],
                "clusters": jsonl_output[idx] 
            }
            json.dump(output, f)
            f.write('\n')

    print(f'Conversion complete. JSONLINES saved to {output_jsonl_file}')

def main(jsonl_file_path):
    doc_names = get_test_file_list_all()
    head_dict = get_head_dict()
    jsonl_output, selected_files, homoname_heads, keys = jsonlines_construct(doc_names, head_dict)


    homoname_dict = dict(zip(selected_files, zip(homoname_heads, jsonl_output)))
    # for key, values in homoname_dict.items():
    #     print(f"{key}: {values}")

    write_jsonlines(jsonl_file_path, selected_files, homoname_heads, jsonl_output, keys)

    # return read_jsonlines(os.path.join(jsonl_file_path, 'homonames_file_with_clusters_total.jsonlines'))

    return homoname_dict



if __name__ == "__main__":
    main('./')
    # get_test_file_list_form_split()
    # get_test_file_list_form_txt()
    # get_head_dict()



# store fixed test dataset link
# find all homo name
# store in dict
# key - doc_key , 
# value - [[ start_idx , end_idx], [..] ,..]
# each has same head _name (col -4) but different entity_number (col -3)
# this is gold
# for pred
# for each doc, all the values in dict
# have diff clu or being marged

# [
#     [
#         [[21, 21]], 
#         [[96, 96], [97, 97]]
#     ], [
#         [[21, 21]], 
#         [[91, 91]], 
#         [[126, 126]]
#     ], [
#         [[21, 21]], 
#         [[116, 116]]
#     ]
# ]

# [
#     [
#         [[150, 150], [475, 475], [671, 671], [672, 672], [675, 675]], 
#         [[635, 635]]
#     ], [
#         [[274, 274]], [[277, 277]]
#     ]
# ]