import os
from typing import List, Optional

import torch
from tqdm.auto import tqdm
from transformers import AutoTokenizer

from refined.offline_data_generation.dataclasses_for_preprocessing import AdditionalEntity
from refined.resource_management.loaders import load_labels, load_wikipedia_to_qcode, load_descriptions, \
    load_qcode_to_idx
from sanskit_utils import get_desc, get_qcode_labels_idx
from generate_s_qcode import build_cluster_id_to_qcode_sanskit
cluster_id_to_qcode = build_cluster_id_to_qcode_sanskit()

# TODO FIX THIS SO IT USES CORRECT QCODE_TO_IDX
def create_description_tensor(output_path: str, qcode_to_idx_filename: str, desc_filename: str, label_filename: str,
                              wiki_to_qcode: str, tokeniser: str = 'roberta-base', is_test: bool = False,
                              include_no_desc: bool = True, keep_all_entities: bool = False,
                              additional_entities: Optional[List[AdditionalEntity]] = None):
    # qcodes = {qcode for qcode in load_wikipedia_to_qcode(wiki_to_qcode).values()}
    labels = load_labels(label_filename, keep_all_entities=keep_all_entities, is_test=is_test)
    # descriptions = load_descriptions(desc_filename, qcodes=qcodes, keep_all_entities=keep_all_entities, is_test=is_test)
    qcode_to_idx = load_qcode_to_idx(qcode_to_idx_filename)
    # qcodes, labels, qcode_to_idx = get_qcode_labels_idx()
    descriptions = get_desc(cluster_id_to_qcode)

    if additional_entities is not None:
        print('Adding labels and descriptions from additional_entities')
        for additional_entity in additional_entities:
            labels[additional_entity.entity_id] = additional_entity.label
            descriptions[additional_entity.entity_id] = additional_entity.description

    # TODO: check no extra [SEP] tokens between label and description or extra [CLS] or [SEP] at end
    # tokenizer = AutoTokenizer.from_pretrained(tokeniser, use_fast=True, add_prefix_space=False)
    muril_model_name = "google/muril-base-cased"
    tokenizer = AutoTokenizer.from_pretrained(muril_model_name,
            add_prefix_space=False,
            use_fast=True,
        )
    length = 128
    print("number of qcode is - ", len(qcode_to_idx))
    descriptions_tns = torch.zeros((len(qcode_to_idx) + 2, length), dtype=torch.int32)
    descriptions_tns.fill_(tokenizer.pad_token_id)

    qcode_has_label = 0
    qcode_has_desc = 0
    i = 0
    for qcode, idx in tqdm(qcode_to_idx.items()):
        if qcode in labels:
            qcode_has_label += 1
            label = labels[qcode]
            if qcode in descriptions and descriptions[qcode] is not None:
                qcode_has_desc += 1
                desc = descriptions[qcode]
            else:
                print("no")
                if not include_no_desc:
                    continue
                desc = 'no description'
            # print(qcode)
            sentence = (label, desc)
            # print(sentence)
            tokenised = tokenizer.encode_plus(sentence, truncation=True, max_length=length, padding='max_length',
                                              return_tensors='pt')['input_ids']
            descriptions_tns[idx] = tokenised
        i += 1
        if i % 500 == 0:
            print(f'QCodes processed {i}, Qcodes with label: {qcode_has_label}, '
                  f'Qcodes with label and description: {qcode_has_desc}')

    torch.save(descriptions_tns, os.path.join(output_path, f'descriptions_tns.pt'))

OUTPUT_PATH = 'data'
create_description_tensor(output_path=OUTPUT_PATH,
                                  qcode_to_idx_filename=os.path.join(OUTPUT_PATH, 'qcode_to_idx.json'),
                                  desc_filename=os.path.join(OUTPUT_PATH, 'desc.json'),
                                  label_filename=os.path.join(OUTPUT_PATH, 'qcode_to_label.json'),
                                  wiki_to_qcode=os.path.join(OUTPUT_PATH, 'enwiki.json'),
                                  additional_entities=None)