import sys

# from refined.offline_data_generation.dataclasses_for_preprocessing import AdditionalEntity
# from refined.offline_data_generation.preprocessing_utils import DENY_CLASSES

sys.path.append('')
from unidecode import unidecode
import logging
import os
import sys
from collections import defaultdict
from typing import Dict, Set, Iterator, Tuple, List, Optional
from random import shuffle
import ujson as json
from tqdm.auto import tqdm
from refined.resource_management.lmdb_wrapper import LmdbImmutableDict
from refined.resource_management.loaders import load_pem, load_qcode_to_idx, load_subclasses, load_redirects, \
    load_wikipedia_to_qcode, load_labels
from sanskit_utils import get_desc, get_qcode_labels_idx
from generate_s_qcode import build_cluster_id_to_qcode_sanskit
# from refined.resource_management.loaders import normalize_surface_form, load_redirects, load_wikipedia_to_qcode, \
#     load_instance_of, remove_wiki_brackets, load_aida_means, load_labels, load_aliases

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
LOG = logging.getLogger(__name__)
EXCLUDE_LIST_AND_DISAMBIGUATION_PAGES = True
maxq = 0
count30 = 0
countmulti = 0
countNone = 0
cluster_id_to_qcode = build_cluster_id_to_qcode_sanskit()

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

def get_pem_map(input_file, map_pem):

    # Read the CoNLL file and process
    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            # Skip empty lines
            # print(line)
            # exit()
            try:
                if line.strip():
                    # Split the line into columns
                    columns = line.split("\t")
                    # Append the 2nd column (index 1) to the text_content list
                    word = columns[2]
                    if len(columns) > 2:
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
                                        global countNone
                                        countNone += 1
                                        # raise Exception("bad indexing")
                                        start_range = int(start_range)
                                        end_range = start_range + len(men)
                                # length = end_range - start_range #+ 1
                                # end_range =  end_range + 1
                                md = word[start_range : end_range]
                                # print(md)

                                # length = len(men)
                                # end_range = start_range + length
                                # md = men

                                surface_form = normalize_surface_form(md)
                                # qcode = str(cluster_id)
                                # if "_0" in cluster_id:
                                #     qcode = "Q" + str(cluster_id.replace('_0', ''))
                                # else:
                                #     qcode = "Q" + str(cluster_id.replace('_', ''))
                                
                                qcode = cluster_id_to_qcode[cluster_id]
                                map_pem[surface_form][qcode] += 1
                                
                                # if md != "janamejaya":
                                #     print()
                                #     print(surface_form)
                                #     print(start_range)
                                #     print(end_range)
                                #     print(length)
                                #     print(qcode)
                                #     exit()
            except:
                # print(input_file)
                print(line)
                # global countNone
                # countNone += 1
                # print(columns)
                # exit()
            # print(line)
    return map_pem

# def call_files_pem():
#     surface_form_to_link_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
#     surface_form_to_link_counts = get_pem_map("vol_1_chapter_1_subchapter_0_1.txt", surface_form_to_link_counts)
#     surface_form_to_link_counts = get_pem_map("vol_1_chapter_2_subchapter_1_1.txt", surface_form_to_link_counts)
#     surface_form_to_link_counts = get_pem_map("vol_1_chapter_3_subchapter_2_1.txt", surface_form_to_link_counts)
#     surface_form_to_link_counts = get_pem_map("vol_1_chapter_4_subchapter_3_1.txt", surface_form_to_link_counts)
#     surface_form_to_link_counts = get_pem_map("vol_1_chapter_4_subchapter_4_2.txt", surface_form_to_link_counts)

#     return surface_form_to_link_counts
def call_files_pem(folder_path: str, test_files):
    surface_form_to_link_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    j = 0
    # Walk through the folder and its subfolders to find all .txt files
    for root, _, files in tqdm(os.walk(folder_path), desc='Reading conll'):
        shuffle(files)
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                # if os.path.basename(file_path) not in test_files:
                surface_form_to_link_counts = get_pem_map(file_path, surface_form_to_link_counts)

    return surface_form_to_link_counts

def get_test_files(test_file_dir):
    with open(test_file_dir, 'r', encoding='utf-8') as file:
        priority_titles = set(line.strip() for line in file if line.strip())
    
    # Separate entries into priority and non-priority lists
    test_files = [os.path.basename(entry) for entry in priority_titles]
    return test_files

def build_pem_lookup_sanskit(output_dir: str):
    # folder_path = "../../../final_data/conll_format/v3"
    folder_path = "../final_data/conll_format/v3_devnagari"
    # Example usage
    test_file_dir = '../final_data/conll_format/test_file_list_v2.txt' 
    test_files = get_test_files(test_file_dir)
    # print(len(test_files))
    surface_form_to_link_counts = call_files_pem(folder_path, test_files)
    # consider taking/storing top 30 only
    pem: Dict[str, Dict[str, float]] = defaultdict(dict)
    for surface_form, qcode_link_counts in tqdm(surface_form_to_link_counts.items(), desc='Writing file'):
        total_link_count = sum(link_count for qcode, link_count in qcode_link_counts.items())
        pem[surface_form] = dict(sorted([(qcode, link_count / total_link_count) for qcode, link_count in
                                         qcode_link_counts.items()], key=lambda x: x[1], reverse=True))

    global maxq
    global count30
    global countmulti
    global countNone
    with open(f'{output_dir}/wiki_pem.json.part', 'w') as output_file:
        for surface_form, qcode_probs in tqdm(pem.items()):
            maxq = max(maxq, len(qcode_probs))
            if len(qcode_probs) >= 30:
                count30 += 1
            if len(qcode_probs) >= 2:
                countmulti += 1
            # qcode_probs = list(qcode_probs.items())
            output_file.write(json.dumps({'surface_form': surface_form, 'qcode_probs': qcode_probs}) + '\n')

    os.rename(f'{output_dir}/wiki_pem.json.part', f'{output_dir}/wiki_pem.json')
    print("max qcode is - ", maxq)
    print("more than 30 qcode count- ", count30)
    print("more than 1 qcode count- ", countmulti)
    print("count invalid range- ", countNone)
    # data_files = resource_manager.get_data_files()
    pem = load_pem(pem_file=os.path.join(output_dir, "wiki_pem.json"), max_cands=None)
    LmdbImmutableDict.from_dict(pem, output_file_path=f"{output_dir}/pem.lmdb")

def title_to_qcode(
        wiki_title: str,
        redirects: Dict[str, str],
        wikipedia_to_qcode: Dict[str, str],
        is_test: bool = False,
) -> Optional[str]:
    wiki_title = (
        wiki_title.replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&le;", "≤")
            .replace("&ge;", "≥")
    )
    wiki_title = wiki_title[0].upper() + wiki_title[1:]
    if wiki_title in redirects:
        wiki_title = redirects[wiki_title]
    if wiki_title in wikipedia_to_qcode:
        qcode = wikipedia_to_qcode[wiki_title]
        return qcode
    return None


# def build_pem_lookup(aligned_wiki_file: str, output_dir: str, resources_dir: str, is_test: bool = False,
#                      add_titles: bool = True,
#                      add_redirects: bool = True, add_aida_means: bool = True, add_labels: bool = True,
#                      add_aliases: bool = True, keep_all_entities: bool = True,
#                      additional_entities: Optional[List[AdditionalEntity]] = None):
    # load lookups
    # redirects = load_redirects(os.path.join(resources_dir, 'redirects.json'), is_test=is_test)
    # instance_of = load_instance_of(os.path.join(resources_dir, 'instance_of_p31.json'), is_test=is_test)
    # wiki_title_to_qcode = load_wikipedia_to_qcode(os.path.join(resources_dir, 'enwiki.json'), is_test=is_test and False)
    # aida_means: Iterator[Tuple[str, str]] = load_aida_means(os.path.join(resources_dir, 'aida_means.tsv.bz2'))

    # wikidata_wikipedia_qcodes: Set[str] = set()
    # for qcode in wiki_title_to_qcode.values():
    #     if qcode is not None and not (qcode in instance_of and len(instance_of[qcode] & DENY_CLASSES) > 0):
    #         wikidata_wikipedia_qcodes.add(qcode)

    # print('len(wikidata_wikipedia_qcodes)', len(wikidata_wikipedia_qcodes))

    # # only add Wikidata entities with a Wikipedia page initially
    # labels: Dict[str, str] = load_labels(os.path.join(resources_dir, 'qcode_to_label.json'),
    #                                      qcodes=wikidata_wikipedia_qcodes,
    #                                      keep_all_entities=keep_all_entities, is_test=is_test)
    # aliases: Dict[str, List[str]] = load_aliases(os.path.join(resources_dir, 'aliases.json'),
    #                                              keep_all_entities=keep_all_entities, qcodes=wikidata_wikipedia_qcodes,
    #                                              is_test=is_test)

    # surface_form_to_link_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # # add additional entities
    # if additional_entities is not None:
    #     for line_num, additional_entity in enumerate(tqdm(additional_entities, desc='Adding additional entities to PEM')):
    #         for surface_form in additional_entity.aliases + [additional_entity.label]:
    #             surface_form = normalize_surface_form(surface_form)
    #             surface_form_to_link_counts[surface_form][additional_entity.entity_id] += 1

    #         # if is_test and line_num > 10000:
    #         #     break

    # # adds titles
    # if add_labels:
    #     line_num = 0
    #     for qcode, surface_form in tqdm(labels.items(), desc='Adding Wikidata labels'):
    #         if 'Q' not in qcode:
    #             continue
    #         if qcode not in wikidata_wikipedia_qcodes and not keep_all_entities:
    #             continue
    #         line_num += 1
    #         if is_test and line_num > 1000:
    #             break
    #         if qcode is not None and not (qcode in instance_of and len(instance_of[qcode] & DENY_CLASSES) > 0):
    #             surface_form = normalize_surface_form(surface_form, remove_the=True)
    #             surface_form_to_link_counts[surface_form][qcode] += 1

    # if add_aliases:
    #     line_num = 0
    #     for qcode, surface_forms in tqdm(aliases.items(), desc='Adding Wikidata aliases'):
    #         line_num += 1
    #         if 'Q' not in qcode:
    #             continue
    #         if is_test and line_num > 1000:
    #             break
    #         for surface_form in surface_forms:
    #             if qcode is not None and not (qcode in instance_of and len(instance_of[qcode] & DENY_CLASSES) > 0):
    #                 surface_form = normalize_surface_form(surface_form, remove_the=True)
    #                 surface_form_to_link_counts[surface_form][qcode] += 1
    # with open(aligned_wiki_file, 'r') as f:
    #     num_pages = 0
    #     for line in tqdm(f, total=6e+6, desc='Adding links'):
    #         line = json.loads(line)
    #         num_pages += 1
    #         for ent in line['hyperlinks_clean']:
    #             if ent['qcode'] in instance_of and len(instance_of[ent['qcode']] & DENY_CLASSES) > 0:
    #                 continue
    #             surface_form = normalize_surface_form(ent['surface_form'], remove_the=True)
    #             surface_form_to_link_counts[surface_form][ent['qcode']] += 1
    #         if is_test and num_pages > 1000:
    #             break

    # if add_titles:
    #     num_pages = 0
    #     for wiki_title, qcode in tqdm(wiki_title_to_qcode.items(), desc='Adding titles'):
    #         num_pages += 1
    #         if not (qcode in instance_of and len(instance_of[qcode] & DENY_CLASSES) > 0):
    #             surface_form = remove_wiki_brackets(normalize_surface_form(wiki_title.replace('_', ' '))
    #                         .replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&le;', '≤')
    #                         .replace('&ge;', '≥'))
    #             surface_form_to_link_counts[surface_form][qcode] += 1

    #         if is_test and num_pages > 1000:
    #             break

    # # add redirects
    # if add_redirects:
    #     for source_title, dest_title in tqdm(redirects.items(), desc='Adding redirects'):
    #         qcode = title_to_qcode(dest_title, redirects=redirects, wikipedia_to_qcode=wiki_title_to_qcode)
    #         if qcode is not None and not (qcode in instance_of and len(instance_of[qcode] & DENY_CLASSES) > 0):
    #             surface_form = remove_wiki_brackets(normalize_surface_form(source_title.replace('_', ' '))
    #                 .replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&le;', '≤')
    #                 .replace('&ge;', '≥'))
    #             surface_form_to_link_counts[surface_form][qcode] += 1

    # if add_aida_means:
    #     line_num = 0
    #     for surface_form, wiki_page in aida_means:
    #         qcode = title_to_qcode(wiki_page, redirects=redirects, wikipedia_to_qcode=wiki_title_to_qcode)
    #         if qcode is not None and not (qcode in instance_of and len(instance_of[qcode] & DENY_CLASSES) > 0):
    #             surface_form = normalize_surface_form(surface_form)
    #             surface_form_to_link_counts[surface_form][qcode] += 1
    #         line_num += 1
    #         if is_test and line_num > 10000:
    #             break

    # TODO add Wikidata labels and Wikidata alias, and crosswikis to includes tables/list links in link counts
    # # consider taking/storing top 30 only
    # pem: Dict[str, Dict[str, float]] = defaultdict(dict)
    # for surface_form, qcode_link_counts in tqdm(surface_form_to_link_counts.items(), desc='Writing file'):
    #     total_link_count = sum(link_count for qcode, link_count in qcode_link_counts.items())
    #     pem[surface_form] = dict(sorted([(qcode, link_count / total_link_count) for qcode, link_count in
    #                                      qcode_link_counts.items()], key=lambda x: x[1], reverse=True))

    # with open(f'{output_dir}/wiki_pem.json.part', 'w') as output_file:
    #     for surface_form, qcode_probs in tqdm(pem.items()):
    #         output_file.write(json.dumps({'surface_form': surface_form, 'qcode_probs': qcode_probs}) + '\n')

    # os.rename(f'{output_dir}/wiki_pem.json.part', f'{output_dir}/wiki_pem.json')

build_pem_lookup_sanskit("data")