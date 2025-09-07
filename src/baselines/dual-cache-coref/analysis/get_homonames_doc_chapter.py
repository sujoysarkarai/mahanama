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

def get_test_file_list_form_all(input_folder = '../../final_data/conll_format/v2_chapter/'):
    
    conll_files = glob.glob(os.path.join(input_folder, '**/*.txt'), recursive=True)
    print("number of files - ",len(conll_files))

    # with open('test_file_list.txt', 'w', encoding='utf-8') as f:
    #     for line in doc_names:
    #         f.write(line)
    #         f.write('\n')
    return conll_files

def get_test_file_list_form_txt(test_txt_file_path= '../../final_data/conll_format/test_file_list_v2.txt'):
    
    with open(test_txt_file_path, 'r', encoding='utf-8') as f:
        doc_names = [line.strip() for line in f.readlines()]
    return doc_names

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

                    if head_word_to_entity_number.get(head_name) is None:  # 1st time
                        head_word_to_entity_number[head_name] = dict()
                    if head_word_to_entity_number.get(head_name).get(entity_number) is None:  # 1st time
                        head_word_to_entity_number[head_name][entity_number] = []
                    head_word_to_entity_number[head_name][entity_number].append([token_number, token_number])

            token_number += 1

    list_homoname_clusters = [] 
    list_homoname_heads = [] 
    for head_name in head_word_to_entity_number.keys():
        if len(head_word_to_entity_number[head_name].keys()) == 1:
            continue
        valid = True
        list_homoname_cluster = []
        for key, value in head_word_to_entity_number[head_name].items():
            list_homoname_cluster.append(value)
        list_homoname_clusters.append(list_homoname_cluster)
        list_homoname_heads.append(head_name)

    return list_homoname_clusters, valid, list_homoname_heads

def print_homo(selected_files, jsonl_output, homoname_heads, idx = 17):
    print(selected_files[idx])
    print(jsonl_output[idx])
    print(homoname_heads[idx])

def jsonlines_construct(file_paths, head_dict, max_tokens = 1024):
    
    jsonl_output = []
    selected_files = []
    homoname_heads = []
    for file_path in tqdm(file_paths):
        json_output, is_vaild, homoname_head = conll_to_json(file_path, head_dict)
        if is_vaild:
            selected_files.append(file_path)
            jsonl_output.append(json_output)
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

    return jsonl_output, selected_files, homoname_heads

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

def write_jsonlines(jsonl_file_path, selected_files, homoname_heads, jsonl_output):
    # Ensure the output directory exists
    output_directory = jsonl_file_path
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Writing to a JSON lines file
    output_jsonl_file = os.path.join(output_directory, 'homonames_file_with_clusters_total_chapter.jsonlines')
    with open(output_jsonl_file, 'w', encoding='utf-8') as f:
        for idx in range(len(jsonl_output)):
            output = {
                "doc_key": selected_files[idx],
                "cluster_head": homoname_heads[idx],
                "clusters": jsonl_output[idx] 
            }
            json.dump(output, f)
            f.write('\n')

    print(f'Conversion complete. JSONLINES saved to {output_jsonl_file}')

def main(jsonl_file_path):
    # doc_names = get_test_file_list_form_all()
    # # doc_names = get_head_dict() # get_test_file_list_form_txt()
    # head_dict = get_head_dict()
    # jsonl_output, selected_files, homoname_heads = jsonlines_construct(doc_names, head_dict)


    # homoname_dict = dict(zip(selected_files, zip(homoname_heads, jsonl_output)))

    # write_jsonlines(jsonl_file_path, selected_files, homoname_heads, jsonl_output)

    return read_jsonlines(os.path.join(jsonl_file_path, 'homonames_file_with_clusters_total_chapter.jsonlines'))

    # return homoname_dict


if __name__ == "__main__":
    main('./')
    # get_test_file_list_form_split()
    # get_test_file_list_form_txt()
    # get_head_dict()

