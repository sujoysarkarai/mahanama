import re
import json
import glob
import os
import random
from tqdm import tqdm
import csv

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

def get_test_file_list_form_split(test_split_file_path= './test_file_with_clusters_split.jsonlines'):
    
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

def split_jsonlines(file_path, base_dir, test_list):

    # # Read the JSON lines file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Shuffle the lines randomly
    random.shuffle(lines)

    # Calculate the number of lines for each split
    test_count = 1000 # int(total_lines * test_ratio)

    test_curr_count = 0
    test_lines = []
    print(len(test_list))

    test_list = [os.path.basename(key) for key in test_list ]

    # Ensure all the test files are selected from the test_list
    for line in tqdm(lines):
        json_line = json.loads(line)
        # Extract the file name from the doc_key
        file_name = os.path.basename(json_line["doc_key"])
        if test_curr_count < test_count and file_name in test_list:
            test_lines.append(line)
            test_curr_count += 1

    # Write the splits to separate files
    # base_dir = './litbank_data3/' # os.path.dirname(file_path)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    test_file = os.path.join(base_dir, 'test_file_with_clusters_split_wo_sandhi.jsonlines')


    with open(test_file, 'w', encoding='utf-8') as f:
        for line in test_lines:
            f.write(line)


    print(f"Data split complete. Files saved to: {test_file}")


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



def conll_to_json(conll_file):
    doc_key = None
    text = []
    clusters = dict()
    clusters_strings = dict()
    open_cluster_mentions = [] # array of [entity_number, start_token_number, position_in_cluster]
    token_number = 0

    with open(conll_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc_key = conll_file
    for line in lines:
        line = line.strip()
        parts = line.split('\t')
        if len(parts) >= 3:
            word = parts[2]

            # Check for clustering annotations
            if len(parts) > 3:
                if "|" in parts[3]:
                    continue
                entities = parts[3].split("|")
                for entity in entities:
                    entity_number = str(entity.replace('(','').replace(')',''))
                    if clusters.get(entity_number) is None:  # 1st time
                        clusters[entity_number] = []
                        clusters_strings[entity_number] = []

                    clusters[entity_number].append([token_number, token_number])
                    clusters_strings[entity_number].append([word])
            text.append(word)
            token_number += 1

    list_cluster = [] # list(clusters.values())
    list_cluster_strings = [] # list(clusters_strings.values())
    for key in list(clusters.keys()):
        list_cluster.append(clusters[key])
        list_cluster_strings.append(clusters_strings[key])
    
    # Prepare JSON object
    output = {
        "doc_key": doc_key,
        "tokens": text,
        "clusters": list_cluster ,
        "clusters_strings": list_cluster_strings
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
    output_jsonl_file = os.path.join(output_directory, 'file_with_clusters_wo_sandhi.jsonlines')
    with open(output_jsonl_file, 'w', encoding='utf-8') as f:
        for json_output in jsonl_output:
            json.dump(json_output, f)
            f.write('\n')

    # print(f'Conversion complete. JSONLINES saved to {output_jsonl_file}')

    test_file_list = get_test_file_list_form_split() #  # get_test_file_list(test_csv_file_path)
    print(len(test_file_list))
    print(test_file_list[1])

    split_jsonlines(output_jsonl_file, jsonl_file_path, test_file_list)


if __name__ == "__main__":
    main('../../final_data/conll_format/v2/', './', '../../final_data/conll_format/list_of_possible_test_subchapters.csv')
