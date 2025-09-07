import os
from typing import List

import torch
from torch.cuda.amp import GradScaler
from torch.optim import AdamW
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup


from refined.data_types.doc_types import Doc
from refined.dataset_reading.entity_linking.wikipedia_dataset import WikipediaDataset
from refined.doc_preprocessing.preprocessor import PreprocessorInferenceOnly
from refined.doc_preprocessing.wikidata_mapper import WikidataMapper
from refined.evaluation.evaluation_error import get_datasets_obj, evaluate
from refined.inference.processor import Refined
from refined.model_components.config import NER_TAG_TO_IX, ModelConfig
from refined.model_components.refined_model import RefinedModel
from refined.resource_management.aws import S3Manager
from refined.resource_management.resource_manager import ResourceManager
from refined.torch_overrides.data_parallel_refined import DataParallelReFinED
from refined.training.fine_tune.fine_tune import run_fine_tuning_loops
from refined.training.train.training_args import parse_training_args
from refined.utilities.general_utils import get_logger

LOG = get_logger(name=__name__)


def main():
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # DDP (ensure batch_elements_included is used)

    training_args = parse_training_args()

    resource_manager = ResourceManager(S3Manager(),
                                       data_dir=training_args.data_dir,
                                       entity_set=training_args.entity_set,
                                       load_qcode_to_title=True,
                                       load_descriptions_tns=True,
                                       model_name=None
                                       )
    if training_args.download_files:
        resource_manager.download_data_if_needed()
        # resource_manager.download_additional_files_if_needed()
        resource_manager.download_training_files_if_needed()

    preprocessor = PreprocessorInferenceOnly(
        data_dir=training_args.data_dir,
        debug=training_args.debug,
        max_candidates=training_args.num_candidates_train,
        transformer_name=training_args.transformer_name,
        ner_tag_to_ix=NER_TAG_TO_IX,  # for now include default ner_to_tag_ix can make configurable in future
        entity_set=training_args.entity_set,
        use_precomputed_description_embeddings=False
    )

    wikidata_mapper = WikidataMapper(resource_manager=resource_manager)
    print(resource_manager.get_training_data_files())
    # exit()

    wikipedia_dataset_file_path = resource_manager.get_training_data_files()['wikipedia_training_dataset']
    # wikipedia_dataset_file_path = wikipedia_dataset_file_path.replace("wikipedia_links_aligned_spans.json", "wikipedia_links_aligned_spans_test2.json")
    
    # print(wikipedia_dataset_file_path)
    # print(training_args)
    # exit()

    eval_docs: List[Doc] = list(iter(WikipediaDataset(
        # start = 0,
        # end = 2,
        start=0,
        end=210,  # first 100 docs are used for eval
        preprocessor=preprocessor,
        resource_manager=resource_manager,
        wikidata_mapper=wikidata_mapper,
        dataset_path=wikipedia_dataset_file_path,
        return_docs=True,  # this means the dataset will return `Doc` objects instead of BatchedElementsTns
        batch_size=1 * training_args.n_gpu,
        num_workers=1,
        prefetch=1,
        mask=0.0,
        random_mask=0.0,
        lower_case_prob=0.0,
        candidate_dropout=0.0,
        sample_k_candidates=30,
        max_mentions= training_args.max_mentions,  # prevents memory issues
        add_main_entity=True  # add weak labels,
    )))

    refined = Refined.from_pretrained(model_name='wikipedia_model_with_numbers',
                                  entity_set='wikipedia',
                                  device=training_args.device, 
                                  use_precomputed_descriptions=False)

    evaluation_metrics = evaluate(refined=refined,
                                  evaluation_dataset_name_to_docs={'WIKI_DEV': eval_docs},
                                  el=True,  # only evaluate EL when training EL
                                  ed=True,  # always evaluate standalone ED
                                  print_errors = False,
                                  ed_threshold=training_args.ed_threshold)


if __name__ == "__main__":
    main()
