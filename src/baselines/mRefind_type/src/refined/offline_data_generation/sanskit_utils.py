import pandas as pd
import json
import os
from tqdm.auto import tqdm

def get_desc(cluster_id_to_qcode):
    #Load the JSON file
    file_path = 'data/cluster_description_KB_version_1_sanskit.json'  # Replace with the actual file name
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create the 'descriptions' map: key = cluster_id, value = description
    # descriptions = {cluster_id_to_qcode[cluster_id]: description for cluster_id, description in data.items()}
    descriptions = dict()
    for cluster_id, description in data.items():
        if cluster_id in cluster_id_to_qcode:
            descriptions[cluster_id_to_qcode[cluster_id]] = description
        else:
            descriptions[cluster_id] = description

    # Print or use the 'descriptions' map
    print("Descriptions Map length:", len(descriptions.keys()))
    return descriptions

# Load the Excel file
def get_qcode_labels_idx():
    file_path = '../final_data/cluster_entity_mention_frequency.xlsx'  # Replace with the actual file name
    df = pd.read_excel(file_path, usecols=[0, 1])  # Only read the first two columns

    # Ensure the column names match those in your file
    # Assuming your columns are "cluster_id" and "head_name"
    df.columns = ['cluster_id', 'head_name']

    # Create the 'labels' map: key = cluster_id, value = head_name
    labels = dict(zip(df['cluster_id'], df['head_name']))

    # Create the 'qcode_to_idx' map: key = cluster_id, value = unique index (position in DataFrame)
    qcode_to_idx = {cluster_id: idx + 1 for idx, cluster_id in enumerate(df['cluster_id'])}
    qcodes = list(labels.keys())
    
    print("qcodes length:", len(qcodes))
    print("qcode_to_idx length:", len(qcode_to_idx.keys()))
    print("labels length:", len(labels.keys()))

    return qcodes, labels, qcode_to_idx

def get_s_qcode(input_file, s_qcode, qcode_count):

    # Read the CoNLL file and process
    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                # Split the line into columns
                columns = line.split("\t")
                if len(columns) > 2:
                    entity_id = columns[3]
                    # print(entity_id)
                    if "(" in entity_id:
                        # print(entity_id, position)
                        for ent in entity_id.split("|"):
                            cluster_id = str(ent.replace('(','').replace(')',''))
                            
                            if "_0" not in cluster_id:
                                if cluster_id in s_qcode:
                                    s_qcode[cluster_id] += 1
                                else:
                                    s_qcode[cluster_id] = 1
                            else:
                                qcode_count.add(cluster_id)
    return s_qcode, qcode_count

def call_files_s_code(folder_path: str):
    s_qcode = dict()
    qcode = set()

    # Walk through the folder and its subfolders to find all .txt files
    for root, _, files in tqdm(os.walk(folder_path), desc='Reading conll'):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                s_qcode, qcode = get_s_qcode(file_path, s_qcode, qcode)

    # print(s_qcode)
    # print(len(qcode))
    return s_qcode, qcode
# q, _ , _ = get_qcode_labels_idx()
# de = get_desc()

# deq = list(de.keys())
# print("in q not in de")
# for i in q:
#     if i not in deq:
#         print(i)
# print("in de not in q")
# for i in deq:
#     if i not in q:
#         print(i)