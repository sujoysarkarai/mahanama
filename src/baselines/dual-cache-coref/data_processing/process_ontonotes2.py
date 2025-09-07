import collections

import re
import json

import conll
from os import path
from constants import SPEAKER_START, SPEAKER_END
from utils import (
    split_into_segments,
    flatten,
    get_sentence_map,
    parse_args,
    normalize_word,
    BaseDocumentState,
)

class OntoNotesDocumentState(BaseDocumentState):
    def __init__(self, key):
        super().__init__(key)
        self.clusters = collections.defaultdict(list)
        self.cluster_heads = collections.defaultdict(list)

    def final_processing(self):
        # populate clusters
        first_subtoken_index = -1
        subtoken_map_hw = flatten(self.segment_subtoken_map)

        for seg_idx, segment in enumerate(self.segment_info):
            for i, tok_info in enumerate(segment):
                first_subtoken_index += 1
                coref = tok_info[-2] if tok_info is not None else "_"

                if coref != "_":
                    last_subtoken_index = first_subtoken_index + tok_info[-1] - 1
                    entities = coref.split("|")
                    cluster_head, cluster_curr_form = self.head_words[subtoken_map_hw[first_subtoken_index]]
                    cluster_head, cluster_curr_form = cluster_head.split("|"), cluster_curr_form.split("|") 
                    char_idx = self.coref_char_idx[subtoken_map_hw[first_subtoken_index]]
                    char_idx = char_idx.split("|")
                    subtok_length = self.subtoken_length[subtoken_map_hw[first_subtoken_index]]
                    # print(subtok_length)
                    # print(char_idx)
                    # print(first_subtoken_index)

                    for entity, head, curr_form, range in zip(entities, cluster_head, cluster_curr_form, char_idx):
                        cluster_id = str(entity.replace('(','').replace(')',''))
                        head = str(head.replace('(','').replace(')',''))
                        curr_form = str(curr_form.replace('(','').replace(')',''))
                        
                        range = str(range.replace('(','').replace(')',''))
                        start_range, end_range = range.split("-")

                        first_subtoken_offset, last_subtoken_offset = get_subtoken_offset(subtok_length, int(start_range), int(end_range))
                        # subtoken level
                        self.clusters[cluster_id].append(
                                        (first_subtoken_index + first_subtoken_offset, first_subtoken_index + last_subtoken_offset)
                                    )

                        # token level
                        # self.clusters[cluster_id].append(
                        #                 (first_subtoken_index, last_subtoken_index)
                        #             )
                        
                        # multi mention model 3 (token + subtoken level)
                        # if len(entities) > 1:
                        #     self.clusters[cluster_id].append(
                        #                 (first_subtoken_index + first_subtoken_offset, first_subtoken_index + last_subtoken_offset)
                        #             )
                        # else:
                        #     self.clusters[cluster_id].append(
                        #                 (first_subtoken_index, last_subtoken_index)
                        #             )
                        self.cluster_heads[cluster_id].append(
                                    [head, curr_form]
                                )
                    char_idx = str(char_idx[0].replace('(','').replace(')','')).split("-")
                    # has multi mention or having a single mention without covering the boundaries
                    if len(entities) > 1 or int(char_idx[1]) - int(char_idx[0]) < sum(subtok_length):
                        # print("multi")
                        self.is_multimention[subtoken_map_hw[first_subtoken_index]] = 1
                        # since sanskrit only have 

        # merge clusters, different for sanskrit because 1 word can have different mention
        # print(sum(self.is_multimention))
        merged_clusters = []
        merged_cluster_heads = []
        # for c1 in self.clusters.keys():
        #     print(c1, self.clusters[c1])
        num_sandhi = 0
        for key in self.clusters.keys():
            c1 = self.clusters[key]
            c_head = self.cluster_heads[key]
        # for c1 in self.clusters.values():
            c1 = set(c1)
            for m in c1:
                for c2 in merged_clusters:
                    if m in c2:
                        num_sandhi += 1
                        break
            merged_clusters.append(c1)
            merged_cluster_heads.append(c_head)

        self.merged_clusters = [list(c) for c in merged_clusters]
        self.merged_cluster_heads = [list(c) for c in merged_cluster_heads]
        all_mentions = flatten(merged_clusters)
        self.sentence_map = get_sentence_map(self.segments, self.sentence_end)
        self.subtoken_map = flatten(self.segment_subtoken_map)

        # get clusters string
        self.clusters_strings = []
        for clu, clu_head in zip(self.merged_clusters, self.merged_cluster_heads):
            clu_str = []
            for men in clu:
                first_subtoken_index, last_subtoken_index = men
                # clu_str.append(
                #             self.words[self.subtoken_map[first_subtoken_index] : self.subtoken_map[last_subtoken_index] + 1]
                #             )
                sub_string = "".join(self.subtokens_words[first_subtoken_index : last_subtoken_index + 1])
                sub_string = sub_string.replace("Ġ", "").replace('##','')
                clu_str.append(
                            [ sub_string ]
                            )
        
            self.clusters_strings.append(clu_str)
        
        # assert len(all_mentions) == len(set(all_mentions)) # in sanskrit len(set(all_mentions)) will be smaller by the ammount of sandhi menion
        assert len(all_mentions) == (len(set(all_mentions)) + num_sandhi)
        num_words = len(flatten(self.segments))
        assert num_words == len(self.subtoken_map), (num_words, len(self.subtoken_map))
        assert num_words == len(self.sentence_map), (num_words, len(self.sentence_map))

    def finalize(self):
        self.final_processing()
        num_words = len(flatten(self.segments))
        assert num_words == len(self.orig_subtoken_map), (
            num_words,
            len(self.orig_subtoken_map),
        )
        return {
            "doc_key": self.doc_key,
            "sentences": self.segments,
            "clusters": self.merged_clusters,
            "sentence_map": self.sentence_map,
            "subtoken_map": self.subtoken_map,
            "orig_subtoken_map": self.orig_subtoken_map,
            "orig_tokens": self.tokens,
        }


def process_speaker(speaker):
    speaker = speaker.replace("_", " ")
    return (" ".join([token.capitalize() for token in speaker.split()])).strip()

def get_subtoken_offset(subtok_length, start_range, end_range):
    curr_idx= 0
    start, end = -1, -1
    for i, length in enumerate(subtok_length):
        if curr_idx + length > start_range and start == -1:
            start = i
        if curr_idx + length > end_range and end == -1:
            end = i
            if start == -1:
                start = 0
            break
        curr_idx += length
    if start == -1:
        start = 0
    if end == -1:
        end = len(subtok_length) - 1
    return start, end

def get_document(document_lines, args):
    document_state = OntoNotesDocumentState(document_lines[0])

    tokenizer = args.tokenizer
    word_idx = -1
    orig_word_idx = -1
    last_speaker = "-"
    for line in document_lines[1]:
        row = line.split()
        sentence_end = len(row) == 0
        if not sentence_end:
            assert len(row) >= 12

            if args.add_speaker:
                speaker = row[9]
                if speaker != last_speaker:
                    word_idx += 1
                    # Insert speaker tokens
                    speaker_str = process_speaker(speaker)
                    document_state.tokens.extend(
                        [SPEAKER_START, speaker_str, SPEAKER_END]
                    )
                    speaker_subtokens = []
                    speaker_subtokens.extend(
                        tokenizer.convert_tokens_to_ids([SPEAKER_START])
                    )
                    speaker_subtokens.extend(
                        tokenizer.convert_tokens_to_ids(tokenizer.tokenize(speaker_str))
                    ),
                    speaker_subtokens.extend(
                        tokenizer.convert_tokens_to_ids([SPEAKER_END])
                    )

                    document_state.token_end += (
                        [False] * (len(speaker_subtokens) - 1)
                    ) + [True]
                    for sidx, subtoken in enumerate(speaker_subtokens):
                        document_state.subtokens.append(subtoken)
                        document_state.info.append(None)
                        document_state.sentence_end.append(False)
                        document_state.subtoken_map.append(word_idx)
                        document_state.orig_subtoken_map.append(-1)

                    last_speaker = speaker

            word_idx += 1
            orig_word_idx += 1
            word = normalize_word(row[3])
            subtokens = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(word))
            document_state.tokens.append(word)
            document_state.token_end += ([False] * (len(subtokens) - 1)) + [True]

            for sidx, subtoken in enumerate(subtokens):
                document_state.subtokens.append(subtoken)
                info = None if sidx != 0 else (row + [len(subtokens)])
                document_state.info.append(info)
                document_state.sentence_end.append(False)
                document_state.subtoken_map.append(word_idx)
                document_state.orig_subtoken_map.append(orig_word_idx)
        else:
            document_state.sentence_end[-1] = True

    split_into_segments(
        document_state,
        args.seg_len,
        document_state.sentence_end,
        document_state.token_end,
    )
    document = document_state.finalize()
    return document


def minimize_partition(split, args):
    input_path = path.join(args.input_dir, "{}.conll".format(split))
    output_path = path.join(
        args.output_dir, "{}.{}.jsonlines".format(split, args.seg_len)
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
                documents.append((doc_key, []))
            elif line.startswith("#end document"):
                continue
            else:
                documents[-1][1].append(line)
    with open(output_path, "w") as output_file:
        for document_lines in documents:
            document = get_document(document_lines, args)
            output_file.write(json.dumps(document))
            output_file.write("\n")
            count += 1
    print("Wrote {} documents to {}".format(count, output_path))


def minimize_split(args):
    tokenizer = args.tokenizer
    if args.add_speaker:
        tokenizer.add_special_tokens(
            {"additional_special_tokens": [SPEAKER_START, SPEAKER_END]}
        )

    for split in ["dev", "test", "train"]:
        minimize_partition(split, args)


if __name__ == "__main__":
    minimize_split(parse_args())
