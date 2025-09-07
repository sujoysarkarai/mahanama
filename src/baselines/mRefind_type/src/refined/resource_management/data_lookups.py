import pickle
from typing import Mapping, List, Tuple, Dict, Any, Set

import numpy as np
import torch
import ujson as json
from nltk import PunktSentenceTokenizer
from transformers import AutoTokenizer, AutoModel, AutoConfig, PreTrainedTokenizer, PreTrainedModel

from refined.resource_management.resource_manager import ResourceManager, get_mmap_shape
from refined.resource_management.aws import S3Manager
from refined.resource_management.lmdb_wrapper import LmdbImmutableDict
from refined.resource_management.loaders import load_human_qcode
import os


class LookupsInferenceOnly:

    def __init__(self, entity_set: str, data_dir: str, use_precomputed_description_embeddings: bool = True,
                 return_titles: bool = False):
        self.entity_set = entity_set
        self.data_dir = data_dir
        self.use_precomputed_description_embeddings = use_precomputed_description_embeddings
        resource_manager = ResourceManager(entity_set=entity_set,
                                           data_dir=data_dir,
                                           model_name=None,
                                           s3_manager=S3Manager(),
                                           load_descriptions_tns=not use_precomputed_description_embeddings,
                                           load_qcode_to_title=return_titles
                                           )
        resource_to_file_path = resource_manager.get_data_files()
        self.resource_to_file_path = resource_to_file_path
        print("resource files-")
        print(resource_to_file_path)
        # exit()

        # replace all get_file and download_if needed
        # always use resource names that are provided instead of relying on same data_dirs
        # shape = (num_ents, max_num_classes)
        # print(get_mmap_shape(resource_to_file_path["qcode_idx_to_class_idx"]))
        # exit()

        # Our np file
        new_filename = "qcode_to_class_tns_5604-8.np"
        directory = os.path.dirname(resource_to_file_path["qcode_idx_to_class_idx"])
        new_path = os.path.join(directory, new_filename)

        # print(resource_to_file_path["qcode_idx_to_class_idx"])
        self.qcode_idx_to_class_idx = np.memmap(
            new_path,
            shape=get_mmap_shape(new_path),
            mode="r",
            dtype=np.int16,
        )
        # self.qcode_idx_to_class_idx = None
        # print("qcode idx to class idx-")
        # print(self.qcode_idx_to_class_idx)
        # print(len(self.qcode_idx_to_class_idx))
        # print(len(self.qcode_idx_to_class_idx[1]))
        # print(self.qcode_idx_to_class_idx[1][0])
        # print(self.qcode_idx_to_class_idx[1])
        # exit()

        if not self.use_precomputed_description_embeddings:
            with open(resource_to_file_path["descriptions_tns"], "rb") as f:
                # (num_ents, desc_len)
                self.descriptions_tns = torch.load(f)
        else:
            # TODO: convert to numpy memmap to save space during training with multiple workers
            self.descriptions_tns = None

        # print("descriptions_tns-")
        # print(self.descriptions_tns.shape)
        # print(self.descriptions_tns[1])
        # exit()

        self.pem: Mapping[str, List[Tuple[str, float]]] = LmdbImmutableDict(resource_to_file_path["wiki_pem"])

        # print(self.pem["superhero"])
        # exit()

        with open(resource_to_file_path["class_to_label"], "r") as f:
            self.class_to_label: Dict[str, Any] = json.load(f)

        # self.class_to_label = None
        # print("class_to_label-")
        # print(self.class_to_label)
        # exit()

        self.human_qcodes: Set[str] = load_human_qcode(resource_to_file_path["human_qcodes"])

        # print("human_qcodes-")
        # print(self.human_qcodes)
        # exit()

        # self.subclasses: Mapping[str, List[str]] = LmdbImmutableDict(resource_to_file_path["subclasses"])
        self.subclasses =None

        # print("subclasses-")
        # print(self.subclasses)
        # exit()

        self.qcode_to_idx: Mapping[str, int] = LmdbImmutableDict(resource_to_file_path["qcode_to_idx"])

        # print("qcode_to_idx-")
        # print(self.qcode_to_idx)
        # exit()

        with open(resource_to_file_path["class_to_idx"], "r") as f:
            self.class_to_idx = json.load(f)

        # print("class_to_idx-")
        # print(self.class_to_idx)
        # exit()

        self.index_to_class = {y: x for x, y in self.class_to_idx.items()}
        self.classes = list(self.class_to_idx.keys())
        self.max_num_classes_per_ent = self.qcode_idx_to_class_idx.shape[1]
        self.num_classes = len(self.class_to_idx)
        # self.index_to_class = None
        # self.classes = None
        # self.max_num_classes_per_ent = None
        # self.num_classes = None

        # print("index_to_class-")
        # print(self.index_to_class)
        # print("max_num_classes_per_ent-")
        # print(self.max_num_classes_per_ent)
        # print("num_classes-")
        # print(self.num_classes)
        # exit()

        if return_titles:
            self.qcode_to_wiki: Mapping[str, str] = LmdbImmutableDict(resource_to_file_path["qcode_to_wiki"])
        else:
            self.qcode_to_wiki = None

        # print("qcode_to_wiki-")
        # print(self.qcode_to_wiki)
        # exit()

        with open(resource_to_file_path["nltk_sentence_splitter_english"], 'rb') as f:
            self.nltk_sentence_splitter_english: PunktSentenceTokenizer = pickle.load(f)

        # print("nltk_sentence_splitter_english-")
        # print(self.nltk_sentence_splitter_english)
        # exit()

        muril_model_name = "google/muril-base-cased"
        self.tokenizers: PreTrainedTokenizer = AutoTokenizer.from_pretrained(muril_model_name,
            add_special_tokens=False,
            add_prefix_space=False,
            use_fast=True,
        )
        self.transformer_model_config = AutoConfig.from_pretrained(muril_model_name)

        # # can be shared
        # self.tokenizers: PreTrainedTokenizer = AutoTokenizer.from_pretrained(
        #     os.path.dirname(resource_to_file_path["roberta_base_model"]),
        #     add_special_tokens=False,
        #     add_prefix_space=False,
        #     use_fast=True,
        # )

        # self.transformer_model_config = AutoConfig.from_pretrained(
        #     os.path.dirname(resource_to_file_path["roberta_base_model"])
        # )

    def get_transformer_model(self) -> PreTrainedModel:
        # cannot be shared so create a copy
        return AutoModel.from_pretrained("google/muril-base-cased")
        # return AutoModel.from_pretrained(
        #     os.path.dirname(self.resource_to_file_path["roberta_base_model"])
        # )
