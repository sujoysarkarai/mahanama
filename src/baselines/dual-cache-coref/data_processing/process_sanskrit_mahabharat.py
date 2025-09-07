import collections

import re
import os
import json

import conll
from os import path
from utils import (
    split_into_segments,
    flatten,
    get_sentence_map,
    parse_args,
    normalize_word,
    BaseDocumentState,
    split_into_segment_multimention,
)
from process_ontonotes2 import OntoNotesDocumentState
import convert_conll_to_txt_sanskrit
import convert_conll_to_txt_sanskrit_chapter
from tqdm import tqdm

count1 = 0

class DocumentState(OntoNotesDocumentState):
    def __init__(self, key):
        super().__init__(key)
        self.clusters = collections.defaultdict(list)

    def finalize(self):
        self.final_processing()
        return {
            "doc_key": self.doc_key,
            "sentences": self.segments,
            "clusters": self.merged_clusters,
            "sentence_map": self.sentence_map,
            "subtoken_map": self.subtoken_map,
            "clusters_strings": self.clusters_strings,
            "cluster_heads": self.merged_cluster_heads,
            "is_multimention" : self.segments_is_multimention,
            "tokens" : self.words,
            "subtokens" : self.subtokens_words,
            "subtoken_length" : self.subtoken_length,
        }


def get_document(document_lines, tokenizer, segment_len):
    document_state = DocumentState(document_lines[0])
    word_idx = -1
    document_state.words = []
    document_state.head_words = []
    document_state.is_multimention = []
    document_state.coref_char_idx = []
    document_state.subtoken_length = []
    document_state.subtokens_words = []
    for line in document_lines[1]:
        row = line.split()
        sentence_end = len(row) == 0
        if not sentence_end:

            # print(row)
            assert len(row) == 8
            if row[3] != "_":
                head_word = [row[4], row[6]]
                char_idx = row[7]
            else:
                head_word = ["" , ""]
                char_idx = ""

            word_idx += 1
            word = normalize_word(row[2])
            # remove extra information
            if len(row) > 4 :
                row = row[:4]


            subtokens = tokenizer.tokenize(word)
            subtok_length = []
            for subtok in subtokens:
                document_state.subtokens_words.append(subtok)
                subtok_length.append(len(subtok.replace('Ġ','')))
            
            subtokens = tokenizer.convert_tokens_to_ids(subtokens)
            document_state.tokens.append(word)
            document_state.token_end += ([False] * (len(subtokens) - 1)) + [True]
            for sidx, subtoken in enumerate(subtokens):
                document_state.subtokens.append(subtoken)
                info = None if sidx != 0 else (row + [len(subtokens)])
                document_state.info.append(info)
                document_state.sentence_end.append(False)
                document_state.subtoken_map.append(word_idx)
            document_state.words.append(word)
            document_state.is_multimention.append(0)
            document_state.head_words.append(head_word)
            document_state.coref_char_idx.append(char_idx)
            document_state.subtoken_length.append(subtok_length)
        else:
            document_state.sentence_end[-1] = True

    split_into_segments(
        document_state,
        segment_len,
        document_state.sentence_end,
        document_state.token_end,
    )

    document = document_state.finalize()
    # print(len(document_state.tokens))
    # print(len(document_state.is_multimention))
    # print(len(document["sentences"][0]), len(document["subtoken_map"]), len(document["is_multimention"]))
    # exit()
    global count1
    count1 += split_into_segment_multimention(document_state)
    
    if len(document_state.segments_is_multimention) > 1:
        print(document_state.doc_key)
    
    # print

    # if "vol_12_chapter_3_subchapter_18_19.txt" in document_state.doc_key:

    return document


def minimize_partition(
    split, cross_val_split, tokenizer, seg_len, input_dir, output_dir
):
    # input_path = path.join(input_dir, "{}/{}.txt".format(cross_val_split, split))
    # output_path = path.join(
    #     output_dir, "{}/{}.{}.jsonlines".format(cross_val_split, split, seg_len)
    # )
    input_path = path.join(input_dir, "{}/{}.txt".format("conll", split))
    output_path = path.join(
        output_dir, "{}.{}.jsonlines".format(split, seg_len)
    )
    output_path_with_cluster_info = path.join(
        output_dir, "{}_info.{}.jsonlines".format(split, seg_len)
    )
    count = 0
    print("Minimizing {}".format(input_path))
    documents = []
    with open(input_path, "r") as input_file:
        for line in input_file.readlines():
            begin_document_match = re.match(conll.BEGIN_DOCUMENT_REGEX, line)
            if begin_document_match:
                doc_key = conll.get_doc_key(
                    begin_document_match.group(1), begin_document_match.group(2)
                )
                # print(doc_key)
                documents.append((doc_key, []))
            elif line.startswith("#end document"):
                # break
                continue
            else:
                documents[-1][1].append(line)
    with open(output_path_with_cluster_info, "w") as output_file_with_cluster_info:
        with open(output_path, "w") as output_file:
            for document_lines in tqdm(documents):
                # print(document_lines[0])
                document = get_document(document_lines, tokenizer, seg_len)

                document["tokens_count"] = [len(flatten(document["is_multimention"])), len(set(document["subtoken_map"]))]
                try:
                    assert len(flatten(document["is_multimention"])) == len(document["tokens"])
                    assert len(flatten(document["is_multimention"])) == len(set(document["subtoken_map"]))
                except:
                    print("assert failed on document - ", document["doc_key"])
                    print("\n\n\n\n")
                output_file_with_cluster_info.write(json.dumps(document))
                output_file_with_cluster_info.write("\n")

                document.pop("clusters_strings", None)
                document.pop("tokens_count", None)
                document.pop("cluster_heads", None)
                document.pop("tokens", None)
                document.pop("subtokens", None)
                document.pop("subtoken_length", None)

                output_file.write(json.dumps(document))
                output_file.write("\n")
                count += 1
    print("Wrote {} documents to {}".format(count, output_path))
    global count1
    print(f"number of multimention in this split: {count1}")
    count1 = 0


def minimize_split(args):
    # args.output_dir = args.input_dir.replace("/conll/", "/longformer/")
    # for cross_val_split in range(10):
    #     # Create cross validation output dir
    #     cross_val_dir = path.join(args.output_dir, str(cross_val_split))
    #     if not path.exists(cross_val_dir):
    #         os.makedirs(cross_val_dir)

        for split in ["dev", "test", "train"]: # ["dual_rama_test"]: #
            minimize_partition(
                split,
                0, # cross_val_split,
                args.tokenizer,
                args.seg_len,
                args.input_dir,
                args.output_dir,
            )


if __name__ == "__main__":
    # convert_conll_to_txt_sanskrit_chapter.main('../../final_data/conll_format/v2_chapter/', '../../coref_resources/data/sanskrit_mahabharat_chapter/conll', '../../final_data/conll_format/list_of_possible_test_subchapters.csv')
    # convert_conll_to_txt_sanskrit.main('../../final_data/conll_format/v2/', '../../coref_resources/data/sanskrit_mahabharat/conll', '../../final_data/conll_format/list_of_possible_test_subchapters.csv')
    # convert_conll_to_txt_sanskrit.main('../../final_data/conll_format/v3/', '../../coref_resources/data/sanskrit_mahabharat_2/conll', '../../final_data/conll_format/list_of_possible_test_subchapters.csv')
    minimize_split(parse_args())
