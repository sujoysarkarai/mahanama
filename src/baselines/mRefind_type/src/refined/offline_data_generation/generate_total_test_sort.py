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
output_file = "data/wikipedia_links_aligned_spans_test.json"
human_qcode = []
class_to_idx = dict()
qcode_to_label : Dict[str, str] = dict()
class_to_label : Dict[str, str] = dict()
curr_class_to_idx_num = 1
# surface_from = set()

def get_id(filename):
    result = "211001"
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

file_path = "../final_data/conll_format/devnagari_test_sort.txt"
process_files(file_path)