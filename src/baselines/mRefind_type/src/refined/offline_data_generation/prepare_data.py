import json
import os
from refined.resource_management.loaders import load_pem, load_labels, load_instance_of
from typing import Set, Dict, List
from random import shuffle
from tqdm.auto import tqdm
from refined.resource_management.lmdb_wrapper import LmdbImmutableDict
from refined.resource_management.loaders import load_pem, load_qcode_to_idx, load_subclasses, load_redirects, \
    load_wikipedia_to_qcode, load_labels
from collections import defaultdict
from unidecode import unidecode
from generate_s_qcode import build_cluster_id_to_qcode_sanskit

cluster_id_to_qcode = build_cluster_id_to_qcode_sanskit()
output_file = "data/output.json"
human_qcode = []
class_to_idx = dict()
qcode_to_label : Dict[str, str] = dict()
class_to_label : Dict[str, str] = dict()
curr_class_to_idx_num = 1
# surface_from = set()

def get_id(filename):
    # Remove the file extension
    base_name = filename.split('.')[0]
    base_name = filename.split('/')[-1]

    # Split the base name into components using '_' as the separator
    parts = base_name.split('_')

    # Extract the numbers for vol, chapter, subchapter, and part
    vol_no = parts[1]       # After 'vol_'
    chapter_no = parts[3]   # After 'chapter_'
    subchapter_no = parts[5] # After 'subchapter_'
    part_no = parts[6]      # After the last part

    # Combine the extracted parts into the desired format
    result = f"{vol_no}0{chapter_no}0{subchapter_no}0{part_no}"
    
    return result

def normalize_surface_form(surface_form: str, remove_the: bool = True):
    # surface_form = surface_form.lower()
    # surface_form = surface_form[4:] if surface_form[:4] == "the " and remove_the else surface_form
    # return (
    #     unidecode(surface_form)
    #     .replace(".", "")
    #     .strip(" ")
    #     .replace('"', "")
    #     # .replace("'s", "")
    #     # .replace("'", "")
    #     .replace("`", "")
    # )
    return surface_form

def get_qcode_from_cluster_id(cluster_id):
    return "Q" + str(cluster_id.replace('_0', ''))

def process_files(input_file):
    
    # Initialize variables
    text_content = []
    span = []
    mcode = []
    hyp = []
    curr_idx = 0

    # Read the CoNLL file and process
    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            # Skip empty lines
            # print(line)
            # exit()
            if line.strip():
                # Split the line into columns
                columns = line.split("\t")
                # Append the 2nd column (index 1) to the text_content list
                word = columns[2]
                if len(columns) > 2:
                    text_content.append(word)
                    word_len = len(word)

                    entity_id = columns[3]
                    # print(entity_id)
                    if "(" in entity_id:
                        position = columns[-1]
                        entity_head = columns[4]
                        mds = columns[6] 
                        # print(entity_id, position)
                        for ent, pos, head, men in zip(entity_id.split("|"), position.split("|"), entity_head.split("|"), mds.split("|")):
                            cluster_id = str(ent.replace('(','').replace(')',''))
                            cluster_head = str(head.replace('(','').replace(')',''))
                            men = str(men.replace('(','').replace(')',''))
                            
                            range = str(pos.replace('(','').replace(')',''))
                            # print(range)
                            start_range, end_range = range.split("-")
                            try:
                                start_range, end_range = int(start_range), int(end_range)
                                end_range = end_range + 1
                            except:
                                # print(men)
                                # print(word)
                                # print(men in word)
                                if men in word:
                                    start_range = word.find(men)
                                    end_range = start_range + len(men)
                                    
                                else: 
                                    start_range = int(start_range)
                                    end_range = start_range + len(men)

                            # length = end_range - start_range + 1
                            # end_range =  end_range + 1
                            md = word[start_range : end_range]

                            # length = len(men)
                            # end_range = start_range + length
                            # md = men

                            surface_form = normalize_surface_form(md)

                            md_span = [
                                curr_idx + start_range, 
                                curr_idx + end_range,
                                surface_form,
                                "MENTION"
                            ]
                            # qcode = str(cluster_id)
                            # qcode = "Q" + str(cluster_id.replace('_0', ''))
                            qcode = cluster_id_to_qcode[cluster_id]
                            md_hyp = {
                                "uri": cluster_head,
                                "surface_form": surface_form,
                                "start": curr_idx + start_range,
                                "end": curr_idx + end_range,
                                "qcode": qcode
                            }
                            if qcode not in human_qcode:
                                human_qcode.append(qcode)
                            global curr_class_to_idx_num
                            if qcode not in class_to_idx:
                                qcode_to_label[qcode] = cluster_head
                                class_to_label[qcode] = cluster_head
                                class_to_idx[qcode] = curr_class_to_idx_num
                                curr_class_to_idx_num += 1

                            hyp.append(md_hyp)
                            span.append(md_span)
                    curr_idx += word_len + 1

    # Prepare the JSON data
    output_data = {
        "id": get_id(input_file),
        "title": input_file.split("/")[-1],  # Extract the file name from the path
        "text": " ".join(text_content),    # Join the words with a space
        "categories": [],
        "hyperlinks": hyp,
        "hyperlinks_clean": hyp,
        "predicted_spans": span
    }
    
    with open(output_file, "a", encoding="utf-8") as json_file:
        json_file.write(json.dumps(output_data) + '\n')

def build_entity_index(pem_filename: str, output_path: str):
    all_qcodes: Set[str] = set()

    pem = load_pem(pem_filename)
    for qcode_probs in tqdm(pem.values()):
        all_qcodes.update(set(qcode_probs.keys()))
    print(len(all_qcodes))
    # exit()

    all_qcodes: Set[str] = set()
    for key in cluster_id_to_qcode.keys():
        all_qcodes.add(cluster_id_to_qcode[key])

    qcode_to_index = {qcode: qcode_idx + 1 for qcode_idx, qcode in enumerate(list(all_qcodes))}

    with open(os.path.join(output_path, 'qcode_to_idx.json.part'), 'w') as fout:
        for k, v in qcode_to_index.items():
            fout.write(json.dumps({'qcode': k, 'index': v}) + '\n')
    os.rename(os.path.join(output_path, 'qcode_to_idx.json.part'), os.path.join(output_path, 'qcode_to_idx.json'))

def build_entity_labels(output_path: str):
    with open(os.path.join(output_path, 'qcode_to_label.json.part'), 'w') as fout:
        global qcode_to_label
        for k, v in qcode_to_label.items():
            fout.write(json.dumps({'qcode': k, 'index': v}) + '\n')
    os.rename(os.path.join(output_path, 'qcode_to_label.json.part'), os.path.join(output_path, 'qcode_to_label.json'))

def build_wiki_to_qcode(output_path: str):
    global qcode_to_label
    wiki_to_qcode = defaultdict(list)
    for qcode, title in qcode_to_label.items():
        wiki_to_qcode[title].append(qcode)
    wiki_to_qcode = dict(wiki_to_qcode)

    wiki_to_qcode = {key: value[0] for key, value in wiki_to_qcode.items()}

    print(len(qcode_to_label), len(wiki_to_qcode))
    with open(os.path.join(output_path, 'wiki_to_qcode.json.part'), 'w') as fout:
        for v, k in wiki_to_qcode.items():
            fout.write(json.dumps({'qcode': k, 'values': v}) + '\n')
    os.rename(os.path.join(output_path, 'wiki_to_qcode.json.part'), os.path.join(output_path, 'wiki_to_qcode.json'))

def call_files_data(folder_path: str, is_test: bool):
    i = 0
    with open(output_file, "w", encoding="utf-8") as json_file:
        json_file.write("")
    # Walk through the folder and its subfolders to find all .txt files
    for root, _, files in tqdm(os.walk(folder_path), desc='Reading conll'):
        shuffle(files)
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                process_files(file_path)
                i += 1
                if is_test and i >= 2:
                    return
    # global surface_from
    # print(len(surface_from))
def add_class_labels():
    with open(os.path.join(OUTPUT_PATH, 'class_to_label.json'), "r") as f:
        class_to_label = json.load(f)
    print(class_to_label)
    # global qcode_to_label
    # for k, v in class_to_label.items():
    #     qcode_to_label[k] = v

folder_path = "../final_data/conll_format/v3_devnagari"

OUTPUT_PATH = 'data'
if not os.path.exists(os.path.join(OUTPUT_PATH, 'qcode_to_idx.json')):
    build_entity_index(os.path.join(OUTPUT_PATH, 'wiki_pem.json'), OUTPUT_PATH)
# build_entity_index(os.path.join(OUTPUT_PATH, 'wiki_pem.json'), OUTPUT_PATH)

test = False
if test:
    call_files_data(folder_path, True)
    exit()
else:
    call_files_data(folder_path, False)

add_class_labels()

if not os.path.exists(os.path.join(OUTPUT_PATH, 'qcode_to_label.json')):
    build_entity_labels(OUTPUT_PATH)
# build_entity_labels(OUTPUT_PATH)

qcode_to_idx = load_qcode_to_idx(filename=os.path.join(OUTPUT_PATH, "qcode_to_idx.json"))
LmdbImmutableDict.from_dict(qcode_to_idx, output_file_path=f"{OUTPUT_PATH}/qcode_to_idx.lmdb")
del qcode_to_idx

qcode_to_wiki = load_qcode_to_idx(os.path.join(OUTPUT_PATH, "qcode_to_idx.json"))
LmdbImmutableDict.from_dict(qcode_to_wiki, output_file_path=f"{OUTPUT_PATH}/qcode_to_wiki.lmdb")

build_wiki_to_qcode(OUTPUT_PATH)
wiki_to_qcode = load_wikipedia_to_qcode(os.path.join(OUTPUT_PATH, "wiki_to_qcode.json"))
LmdbImmutableDict.from_dict(wiki_to_qcode, output_file_path=f"{OUTPUT_PATH}/wiki_to_qcode.lmdb")

qcode_to_label = load_qcode_to_idx(filename=os.path.join(OUTPUT_PATH, "qcode_to_label.json"))
LmdbImmutableDict.from_dict(qcode_to_label, output_file_path=f"{OUTPUT_PATH}/qcode_to_label.lmdb")

# with open(os.path.join(OUTPUT_PATH, "human_qcodes.json"), "w", encoding="utf-8") as file:
#     for q in human_qcode:
#         file.write(q + "\n")
# with open(os.path.join(OUTPUT_PATH, "class_to_idx.json"), "w", encoding="utf-8") as file:
#     text = str(class_to_idx)
#     text = text.replace("'", "\"")
#     file.write(text)     
# with open(os.path.join(OUTPUT_PATH, "class_to_label.json"), "w", encoding="utf-8") as file:  
#     text = str(class_to_label)
#     text = text.replace("'", "\"")
#     file.write(text) 