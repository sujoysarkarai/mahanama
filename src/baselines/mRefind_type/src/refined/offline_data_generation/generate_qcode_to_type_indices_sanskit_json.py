import json
import random
import os
import csv
import pandas as pd
from generate_s_qcode import build_cluster_id_to_qcode_sanskit
from collections import defaultdict
import logging
import sys
from typing import Dict, Set, Any, List, Optional

import torch
import ujson as json
from tqdm.auto import tqdm

import numpy as np

from refined.doc_preprocessing.class_handler import ClassHandler
from refined.offline_data_generation.dataclasses_for_preprocessing import AdditionalEntity
from refined.resource_management.loaders import load_subclasses, load_instance_of, load_occuptations, \
    load_sports, load_country, load_qcode_to_idx

# Create a defaultdict where the default value is an empty set
class_code_to_class_name = {}
class_code_to_class_idx = {}
class_name_to_class_qcode = {}
resources_dir = "data"
human_class_name = ["Person"]

def create_class_to_idx(chosen_classes_file: str) -> Dict[str, int]:
    chosen_classes = []
    with open(chosen_classes_file, 'r') as f:
        for line in f:
            chosen_classes.append(line.rstrip('\n'))
    return {chosen_class: cls_idx + 1 for cls_idx, chosen_class in enumerate(chosen_classes)}

def human_qcode(qcode_to_class_type_names, is_test: bool = False):
    class_to_idx: Dict[str, int] = create_class_to_idx(os.path.join(resources_dir, 'chosen_classes.txt'))
    chosen_classes: Set[str] = set(class_to_idx.keys())

    qcode_to_idx = load_qcode_to_idx(os.path.join(resources_dir, 'qcode_to_idx.json'))

    humam_class_qcode = set()
    for n, q in class_name_to_class_qcode.items():
        if n in human_class_name:
            humam_class_qcode.add(class_name_to_class_qcode[n])

    # get max length to determine size of tensor
    with open(os.path.join(resources_dir, "human_qcodes.json"), "w", encoding="utf-8") as file:
        for qcode, qcode_idx in tqdm(qcode_to_idx.items(), desc='Determining max number of classes'):
            classes = get_qcode_classes(qcode, qcode_to_class_type_names)
            
            if len(humam_class_qcode.intersection(classes)) > 0:
                file.write(qcode + "\n")

def create_tensors(qcode_to_class_type_names, is_test: bool = False):
    class_to_idx: Dict[str, int] = create_class_to_idx(os.path.join(resources_dir, 'chosen_classes.txt'))
    chosen_classes: Set[str] = set(class_to_idx.keys())

    qcode_to_idx = load_qcode_to_idx(os.path.join(resources_dir, 'qcode_to_idx.json'))

    print(class_to_idx)
    # get max length to determine size of tensor
    i = 0
    max_classes_ln = 0
    for qcode, qcode_idx in tqdm(qcode_to_idx.items(), desc='Determining max number of classes'):
        classes = get_qcode_classes(qcode, qcode_to_class_type_names)
        classes_idx = [class_to_idx[c] for c in classes]
        if len(classes_idx) > max_classes_ln:
            max_classes_ln = len(classes_idx)
        i += 1
        # if i > 100 and is_test:
        #     break

    qcode_to_class_idx: torch.Tensor = torch.zeros(size=(len(qcode_to_idx) + 2, max_classes_ln + 2), dtype=torch.int16)
    print(qcode_to_class_idx.shape)

    # fill tensor
    has_class = 0
    no_class = 0
    for qcode, qcode_idx in tqdm(qcode_to_idx.items(), desc='Filling qcode_to_class_idx tensor'):
        classes = get_qcode_classes(qcode, qcode_to_class_type_names)
        classes_idx = [class_to_idx[c] for c in classes]
        if len(classes_idx) == 9:
            print(qcode)
            print(classes_idx)
        qcode_to_class_idx[qcode_idx, :len(classes_idx)] = torch.tensor(classes_idx)
        if len(classes_idx) > 0:
            has_class += 1
        else:
            no_class += 1
        i += 1
        # if i > 100 and is_test:
        #     break

    print(f'Has class: {has_class}, no class: {no_class}, {has_class / (has_class + no_class) * 100}%')
    print('qcode_to_class_idx row 0-10', list(enumerate(qcode_to_class_idx[:10])))
    print('qcode_to_idx row 0-10', list(enumerate(list(qcode_to_idx.items())[:10])))
    print('class_to_idx row 0-10', list(enumerate(list(class_to_idx.items())[:10])))
    torch.save(qcode_to_class_idx, f'{resources_dir}/qcode_to_class_tns.pt')

    qcode_to_class_np = np.memmap(f"{resources_dir}/qcode_to_class_tns_{qcode_to_class_idx.size(0)}-{qcode_to_class_idx.size(1)}.np",
                                  shape=qcode_to_class_idx.size(),
                                  dtype=np.int16,
                                  mode='w+')
    qcode_to_class_np[:] = qcode_to_class_idx[:]
    qcode_to_class_np.flush()

    # qcode_to_class_idx.numpy().tofile(f'{resources_dir}/qcode_to_class_tns.np')
    # with open(f'{resources_dir}/qcode_to_idx.json', 'w') as f:
    #     json.dump(qcode_to_idx, f)
    with open(f'{resources_dir}/class_to_idx.json', 'w') as f:
        json.dump(class_to_idx, f)


def get_qcode_classes(qcode: str, qcode_to_class_type_names) \
        -> Set[str]:
    class_qcode = set()
    for n in qcode_to_class_type_names[qcode]:
        class_qcode.add(class_name_to_class_qcode[n])
    return class_qcode

def class_selection(class_type_file):
    i = 0
    with open(class_type_file, "r") as file:
        for line in file:
            # Split the line into two parts based on TAB
            name = line.strip()
            cqcode = "Q555" + str(i)
            class_name_to_class_qcode[name] = cqcode
            i += 1

    with open(os.path.join(resources_dir, 'chosen_classes.txt.part'), 'w') as f_out:
        f_out.write('\n'.join([x for x in class_name_to_class_qcode.values()]))
    os.rename(os.path.join(resources_dir, 'chosen_classes.txt.part'),
              os.path.join(resources_dir, 'chosen_classes.txt'))

def get_class_type(ner_type_file):
    # Read the CSV file
    qcode_to_class_type_names = defaultdict(set)
    with open(ner_type_file, "r") as f:
        class_to_label: Dict[str, Any] = json.load(f)
        
    for k, v in class_to_label.items():
        cluster_id = k
        if cluster_id in cluster_id_to_qcode:
            # try:
            class_names = set(v)
            qcode_to_class_type_names[cluster_id_to_qcode[cluster_id]].update(class_names)
            # except:
            #     pass
        # exit()
    # print(qcode_to_class_type_names)
    return qcode_to_class_type_names

def build_entity_index(pem_filename: str, output_path: str):
    all_qcodes: Set[str] = set()

    # pem = load_pem(pem_filename)
    # for qcode_probs in tqdm(pem.values()):
    #     all_qcodes.update(set(qcode_probs.keys()))
    for key in cluster_id_to_qcode.keys():
        all_qcodes.add(cluster_id_to_qcode[key])

    qcode_to_index = {qcode: qcode_idx + 1 for qcode_idx, qcode in enumerate(list(all_qcodes))}
    qcode_length = len(qcode_to_index)
    # for i, q in enumerate(class_name_to_class_qcode.values()):
    #     if q in qcode_to_index.keys():
    #         print(q)
    #         print("error")
    #         exit()
    #     qcode_to_index[q] = i + qcode_length + 1

    with open(os.path.join(output_path, 'qcode_to_idx.json.part'), 'w') as fout:
        for k, v in qcode_to_index.items():
            fout.write(json.dumps({'qcode': k, 'index': v}) + '\n')
    os.rename(os.path.join(output_path, 'qcode_to_idx.json.part'), os.path.join(output_path, 'qcode_to_idx.json'))

def build_class_labels(resources_dir: str):
    with open(os.path.join(resources_dir, 'chosen_classes.txt'), 'r') as f:
        chosen_classes = {l.rstrip('\n') for l in f.readlines()}

    labels = {qcode: name for name, qcode in class_name_to_class_qcode.items()} # load_labels(os.path.join(resources_dir, 'qcode_to_label.json'), False)
    cls_to_label: Dict[str, str] = dict()
    for cls in chosen_classes:
        if cls in labels:
            cls_to_label[cls] = labels[cls]
        else:
            cls_to_label[cls] = cls
    with open(f'{resources_dir}/class_to_label.json', 'w') as f:
        json.dump(cls_to_label, f)

    logging.info('Written class to label')

# Example usage
# ner_type_file = '../final_data/conll_format/cluster_head_to_ner_label.json'  
ner_type_file = '../final_data/conll_format/cluster_head_to_type_label.json'
class_type_file = '../final_data/conll_format/classes_json_types.txt'  # Replace with your titles file path

cluster_id_to_qcode = build_cluster_id_to_qcode_sanskit()
class_selection(class_type_file)
print(class_code_to_class_name)
build_entity_index(os.path.join(resources_dir, 'wiki_pem.json'), resources_dir)
qcode_to_class_type_names = get_class_type(ner_type_file)

create_tensors(qcode_to_class_type_names)
human_qcode(qcode_to_class_type_names)
build_class_labels(resources_dir)