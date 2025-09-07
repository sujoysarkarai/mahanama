import re
import json
import glob
import os
import random
from tqdm import tqdm
import csv
from convert_p import load_data_gn, load_data

data_g_map, data_n_map = load_data_gn()
data_map = load_data()
comp_count = {"same_cluster_total_match":0, "same_cluster_part_match":0, "same_cluster_miss_match":0, "diff_cluster_total_match":0, "diff_cluster_part_match":0, "diff_cluster_miss_match":0, "missing":0}

def check_men_comp(men1, men2, is_same_cluster):
    men1, men2 = men1[0], men2[0]
    if men1 not in data_map or men2 not in data_map: 
        comp_count['missing'] += 1
        print("missing - ", men1, men2)
        return 

    men1_type = data_map[men1]
    men2_type = data_map[men2]

    if len(men1_type) == 0 or len(men2_type) == 0: # or len(men1_g) == 0 or len(men2_g) == 0: 
        comp_count['missing'] += 1
        return
    
    union_type = men1_type.union(men2_type)
    inter_type = men1_type.intersection(men2_type)

    if len(union_type) == len(men1_type) or len(union_type) == len(men2_type):
        if is_same_cluster:
            comp_count['same_cluster_total_match'] += 1
        else:
            comp_count['diff_cluster_total_match'] += 1
    elif len(inter_type) > 0:
        if is_same_cluster:
            comp_count['same_cluster_part_match'] += 1
        else:
            comp_count['diff_cluster_part_match'] += 1
    else:
        if is_same_cluster:
            comp_count['same_cluster_miss_match'] += 1
        else:
            comp_count['diff_cluster_miss_match'] += 1

def check_men_comp_gn(men1, men2, is_same_cluster):
    men1, men2 = men1[0], men2[0]
    if men1 not in data_g_map or men1 not in data_n_map or men2 not in data_g_map or men2 not in data_n_map: 
        comp_count['missing'] += 1
        print("missing - ", men1, men2)
        return 

    men1_g, men1_n = data_g_map[men1], data_n_map[men1]
    men2_g, men2_n = data_g_map[men2], data_n_map[men2]

    if len(men1_n) == 0 or len(men2_n) == 0: # or len(men1_g) == 0 or len(men2_g) == 0: 
        comp_count['missing'] += 1
        return
    
    union_g = men1_g.union(men2_g)
    union_n = men1_n.union(men2_n)
    inter_g = men1_g.intersection(men2_g)
    inter_n = men1_n.intersection(men2_n)

    if len(men1_g) > 0 and len(men2_g) > 0 and (len(union_g) == len(men1_g) or len(union_g) == len(men2_g)) and (len(union_n) == len(men1_n) or len(union_n) == len(men2_n)):
        if is_same_cluster:
            comp_count['same_cluster_total_match'] += 1
        else:
            comp_count['diff_cluster_total_match'] += 1
    elif ((len(men1_g) == 0 and len(men2_g) == 0) or len(inter_g) > 0) and len(inter_n) > 0:
        if is_same_cluster:
            comp_count['same_cluster_part_match'] += 1
        else:
            comp_count['diff_cluster_part_match'] += 1
    else:
        if is_same_cluster:
            comp_count['same_cluster_miss_match'] += 1
        else:
            comp_count['diff_cluster_miss_match'] += 1

def check_per_cluster_comp(clu, rest_clu):
    num_men = len(clu)
    for i in range(num_men):
        # same cluster mentions
        for men_j in clu[i+1:]:
            check_men_comp(clu[i], men_j, True)
    
        # diff cluster mentions
        for rest_c in rest_clu:
            for men in rest_c:
                check_men_comp(clu[i], men, False)

def check_cluster_comp(cluster):
    num_clu = len(cluster)
    for x in range(num_clu):
        if x == num_clu - 1:
            check_per_cluster_comp(cluster[x], [])
        else:
            check_per_cluster_comp(cluster[x], cluster[x+1:])

def check_split_comp(split_data):
    for line in tqdm(split_data):
        json_line = json.loads(line)
        cluster = json_line['clusters_strings']
        check_cluster_comp(cluster)

def comp_print_info():
    print(comp_count)
    same_cluster_cnt = comp_count['same_cluster_total_match'] + comp_count['same_cluster_miss_match'] + comp_count['same_cluster_part_match']
    same_cluster_total_match_p = comp_count['same_cluster_total_match']/ same_cluster_cnt
    same_cluster_part_match_p = comp_count['same_cluster_part_match']/ same_cluster_cnt
    same_cluster_miss_match_p = comp_count['same_cluster_miss_match']/ same_cluster_cnt
    print("same cluster total match % - ", same_cluster_total_match_p, " part match % - ", same_cluster_part_match_p, " miss match % - ", same_cluster_miss_match_p)

    diff_cluster_cnt = comp_count['diff_cluster_total_match'] + comp_count['diff_cluster_miss_match'] + comp_count['diff_cluster_part_match']
    diff_cluster_total_match_p = comp_count['diff_cluster_total_match']/ diff_cluster_cnt
    diff_cluster_part_match_p = comp_count['diff_cluster_part_match']/ diff_cluster_cnt
    diff_cluster_miss_match_p = comp_count['diff_cluster_miss_match']/ diff_cluster_cnt
    print("diff cluster total match % - ", diff_cluster_total_match_p, " part match % - ", diff_cluster_part_match_p, " miss match % - ", diff_cluster_miss_match_p)

    total_cnt = comp_count['same_cluster_total_match'] + comp_count['same_cluster_miss_match'] + comp_count['diff_cluster_total_match'] + comp_count['diff_cluster_miss_match'] + comp_count['missing'] + comp_count['same_cluster_part_match'] + comp_count['diff_cluster_part_match']
    missing_p = comp_count['missing']/total_cnt
    print("total cnt - ", total_cnt)
    print("missing % - ", missing_p)

def remove_singleton(cluster, cluster_string, cluster_head):
    updated_cluster = []
    updated_cluster_string = []
    updated_cluster_head = []
    for clu, clu_str, clu_head in zip(cluster, cluster_string, cluster_head):
        if len(clu) == 1:
            continue
        updated_cluster.append(clu)
        updated_cluster_string.append(clu_str)
        updated_cluster_head.append(clu_head)
    return updated_cluster, updated_cluster_string, updated_cluster_head

def get_doc_key(lines):
    json_lines = [json.loads(line) for line in lines]
    doc_key_lines = [line["doc_key"] for line in json_lines]
    return doc_key_lines

def get_test_file_list(test_csv_file_path):
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

def get_test_file_list_form_split(test_split_file_path= './test.4096.jsonlines'):
    
    with open(test_split_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    doc_names = get_doc_key(lines)
    doc_names = [file_name[:-2] if file_name.endswith('_0') else file_name for file_name in doc_names]
    # with open('test_file_list.txt', 'w', encoding='utf-8') as f:
    #     for line in doc_names:
    #         f.write(line)
    #         f.write('\n')
        
    return doc_names

def get_test_file_list_txt(test_txt_file_path = '../../final_data/conll_format/test_file_list_v2.txt'):
    # Initialize an empty list to store the base file names
    file_names = []

    # Open and read the .txt file
    with open(test_txt_file_path, mode='r') as file:
        lines = file.readlines()
        for line in lines:
            # Strip any surrounding whitespace (including newlines)
            cleaned_line = line.strip()
            # Extract the base filename
            base_name = os.path.basename(cleaned_line)
            # Add the base filename to the list
            file_names.append(base_name)

    return file_names

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
    test_count = 1000 # int(total_lines * test_ratio)

    test_curr_count = 0
    test_lines = []
    remaining_lines = []
    print(len(test_list))

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

    check_split_comp(test_lines)
    comp_print_info()

    check_split_comp(train_lines)
    check_split_comp(val_lines)
    comp_print_info()

def split_document(doc, max_tokens=1024):
    """
    Splits a document into multiple smaller documents if it exceeds max_tokens.
    Adjusts the clusters accordingly.
    """
    tokens = doc['tokens']
    clusters = doc['clusters']
    clusters_strings = doc['clusters_strings']
    clusters_heads = doc['cluster_head']
    doc_key = doc['doc_key']
    
    # List to hold split documents
    split_docs = []
    # print(clusters)
    
    # Split tokens into chunks of size max_tokens
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_clusters = []
        chunk_clusters_strings = []
        chunk_clusters_heads = []
        
        # Adjust clusters for the current chunk
        for cluster, cluster_string, clusters_head in zip(clusters, clusters_strings, clusters_heads):
            new_cluster = []
            new_cluster_strings = []
            new_cluster_heads = []
            for position, position_String, position_head in zip(cluster, cluster_string, clusters_head):
                start, end = position
                # Check if cluster falls within the current chunk
                if end <= i:
                    continue
                if start >= i + max_tokens:
                    break
                    
                new_cluster.append([start - i , end - i])
                new_cluster_strings.append(position_String)
                new_cluster_heads.append(position_head)
                
            if new_cluster:
                chunk_clusters.append(new_cluster)
                chunk_clusters_strings.append(new_cluster_strings)
                chunk_clusters_heads.append(new_cluster_heads)
        
        # chunk_clusters, chunk_clusters_strings, chunk_clusters_heads = remove_singleton(chunk_clusters, chunk_clusters_strings, chunk_clusters_heads)
        # Create a new document for the current chunk
        split_doc = {
            "doc_key": f"{doc_key}_part_{len(split_docs)}",
            "tokens": chunk_tokens,
            "clusters": chunk_clusters,
            "clusters_strings": chunk_clusters_strings,
            "cluster_heads": chunk_clusters_heads
        }
        split_docs.append(split_doc)
    
    return split_docs



def conll_to_json(conll_file):
    doc_key = None
    text = []
    clusters = dict()
    clusters_strings = dict()
    open_cluster_mentions = [] # array of [entity_number, start_token_number, position_in_cluster]
    token_number = 0
    cluster_heads = dict()

    with open(conll_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc_key = conll_file
    for line in lines:
        line = line.strip()
        parts = line.split('\t')
        if len(parts) >= 3:
            word = parts[2]
            text.append(word)

            # Check for clustering annotations
            if len(parts) > 3 and parts[4] != "_": # and "|" not in parts[4]:
                entities = parts[3].split("|")
                heads = parts[4].split("|")
                curr_forms = parts[5].split("|")
                for entity, head, curr_form in zip(entities, heads, curr_forms):
                    entity_number = str(entity.replace('(','').replace(')',''))
                    head = str(head.replace('(','').replace(')',''))
                    curr_form = str(curr_form.replace('(','').replace(')',''))
                    
                    if clusters.get(entity_number) is None:  # 1st time
                        clusters[entity_number] = []
                        clusters_strings[entity_number] = []
                        
                        cluster_heads[entity_number] = []

                    # if [token_number, token_number] in clusters[entity_number]:
                    #     continue
                    clusters[entity_number].append([token_number, token_number])
                    clusters_strings[entity_number].append([word])
                    cluster_heads[entity_number].append([head, curr_form])
                    # if '(' in entity and ')' in entity:
                    #     clusters[entity_number].append([token_number, token_number])
                    #     clusters_strings[entity_number].append([word])
                    # elif '(' in entity:
                    #     open_cluster_mentions.append([entity_number, token_number, len(clusters_strings[entity_number])])
                    #     clusters_strings[entity_number].append([])
                    # else:
                    #     for i in reversed(open_cluster_mentions):
                    #         entity_number_in_open_cluster, start_token_number, position_in_cluster = i
                    #         if entity_number_in_open_cluster == entity_number:
                    #             clusters[entity_number].append([start_token_number, token_number])
                    #             clusters_strings[entity_number][position_in_cluster].append(word)
                    #             open_cluster_mentions.remove(i)
                    #             break
                
            # for i in open_cluster_mentions:
            #     entity_number_in_open_cluster, start_token_number, position_in_cluster = i
            #     clusters_strings[entity_number_in_open_cluster][position_in_cluster].append(word)

            token_number += 1

    list_cluster = [] # list(clusters.values())
    list_cluster_strings = [] # list(clusters_strings.values())
    list_cluster_heads = []
    for key in list(clusters.keys()):
        list_cluster.append(clusters[key])
        list_cluster_strings.append(clusters_strings[key])
        list_cluster_heads.append(cluster_heads[key])
    
    # Prepare JSON object
    output = {
        "doc_key": doc_key,
        "tokens": text,
        "clusters": list_cluster ,
        "clusters_strings": list_cluster_strings,
        "cluster_heads": list_cluster_heads
    }

    return output


def jsonlines_construct(folder_path, max_tokens = 1024):
    file_paths = glob.glob(os.path.join(folder_path, '**/*.txt'), recursive=True)
    
    # file_paths = ['../final_data/conll_format/v1/vol_1_chapter_2_subchapter_1_1.txt']
    jsonl_output = []
    for file_path in tqdm(file_paths):
        json_output = conll_to_json(file_path)
        jsonl_output.append(json_output)
    
    return jsonl_output

    split_documents_jsonl_output = []
    
    for doc in jsonl_output:
        doc_len = len(doc['tokens']) # + 4 * len([clu for clu in doc['clusters']]) + len(doc['doc_key'])
        
        if doc_len >= max_tokens:
            # print(doc_len)
            split_docs = split_document(doc, max_tokens)
            split_documents_jsonl_output.extend(split_docs)
        else:
            split_documents_jsonl_output.append(doc)

    print(len(split_documents_jsonl_output))
    return split_documents_jsonl_output


def main(conll_files_path, jsonl_file_path, test_csv_file_path):
    jsonl_output = jsonlines_construct(conll_files_path)

    # Ensure the output directory exists
    output_directory = jsonl_file_path
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Writing to a JSON lines file
    output_jsonl_file = os.path.join(output_directory, 'file_with_clusters.jsonlines')
    with open(output_jsonl_file, 'w', encoding='utf-8') as f:
        for json_output in jsonl_output:
            json.dump(json_output, f)
            f.write('\n')

    print(f'Conversion complete. JSONLINES saved to {output_jsonl_file}')

    test_file_list = get_test_file_list_txt() # get_test_file_list_form_split() #  # get_test_file_list(test_csv_file_path)

    split_jsonlines(output_jsonl_file, jsonl_file_path, test_file_list)


if __name__ == "__main__":
    main('../../final_data/conll_format/v3/', './', '../../final_data/conll_format/list_of_possible_test_subchapters.csv')
