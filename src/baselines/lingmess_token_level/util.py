import os
import logging
import json
import spacy
from pathlib import Path
from tqdm import tqdm
import random
import pandas as pd
import torch
import numpy as np
import vibhuki_number
from consts import NULL_ID_FOR_COREF, CATEGORIES, PRONOUNS_GROUPS, STOPWORDS
from vibhukti_get import generate_forms, suffixes_dict, are_words_similar
from prepare_sanskrit_mahabharat.convert_p import load_data as get_token_to_category_map
from prepare_sanskrit_mahabharat.convert_p import load_data_gn as get_token_to_category_map_gn

logger = logging.getLogger(__name__)
nlp = None
g_print_count_re = 0
token_to_category_map = get_token_to_category_map("prepare_sanskrit_mahabharat/token_to_category.jsonl")
token_to_category_map_g, token_to_category_map_n = get_token_to_category_map_gn("prepare_sanskrit_mahabharat/token_to_category_gn.jsonl")

def output_evaluation_metrics(metrics_dict, output_dir, prefix):
    loss = metrics_dict['loss']
    post_pruning_mention_pr, post_pruning_mentions_r, post_pruning_mention_f1 = metrics_dict['post_pruning'].get_prf()
    mention_p, mentions_r, mention_f1 = metrics_dict['mentions'].get_prf()
    total_p, total_r, total_f1 = metrics_dict['coref'].get_prf()
    muc_p, muc_r, muc_f1 = metrics_dict['coref'].get_metric_prf(metric = 'muc')
    b_cubed_p, b_cubed_r, b_cubed_f1 = metrics_dict['coref'].get_metric_prf(metric = 'b_cubed')
    ceafe_p, ceafe_r, ceafe_f1 = metrics_dict['coref'].get_metric_prf(metric = 'ceafe')
    results = {
        'eval_loss': loss,
        "post pruning mention precision": post_pruning_mention_pr,
        "post pruning mention recall": post_pruning_mentions_r,
        "post pruning mention f1": post_pruning_mention_f1,
        "mention precision": mention_p,
        "mention recall": mentions_r,
        "mention f1": mention_f1,
        "total_precision": total_p,
        "total_recall": total_r,
        "total_f1": total_f1,
        "muc_precision": muc_p,
        "muc_recall": muc_r,
        "muc_f1": muc_f1,
        "b_cubed_precision": b_cubed_p,
        "b_cubed_recall": b_cubed_r,
        "b_cubed_f1": b_cubed_f1,
        "ceafe_precision": ceafe_p,
        "ceafe_recall": ceafe_r,
        "ceafe_f1": ceafe_f1
    }
    results = {**results, **metrics_dict['coref_categories'].get_stats()}

    logger.info("***** Eval results {} *****".format(prefix))
    for key, value in results.items():
        if isinstance(value, float):
            logger.info(f"  {key : <30} = {value:.3f}")
            print(f"  {key : <30} = {value:.3f}")
        elif isinstance(value, dict):
            # if value['true_pairs'] != 0 or value['false_pairs'] != 0:
                logger.info(f"  {key : <30} = {value}")
                print(f"  {key : <30} = {value}")

    return results


def align_clusters(clusters, subtoken_maps, new_word_maps):
    new_clusters = []
    for cluster in clusters:
        new_cluster = []
        for start, end in cluster:
            try:
                start, end = subtoken_maps[start], subtoken_maps[end]
            except IndexError:
                # this is padding index
                continue
            if start is None or end is None:
                continue
            start, end = new_word_maps[start], new_word_maps[end]
            new_cluster.append([start, end])
        new_clusters.append(new_cluster)
    return new_clusters


def flatten(l):
    return [item for sublist in l for item in sublist]


def read_jsonlines(file):
    with open(file, 'r') as f:
        docs = [json.loads(line.strip()) for line in f]
    return docs


def write_prediction_to_jsonlines(args, doc_to_prediction, doc_to_tokens, doc_to_subtoken_map, doc_to_new_word_map):
    eval_file = args.dataset_files[args.eval_split]
    if args.output_file is not None:
        output_eval_file = args.output_file
    else:
        output_eval_file = Path(eval_file).stem + '.output.jsonlines'
        if args.output_dir is not None:
            output_eval_file = os.path.join(args.output_dir, output_eval_file)
    logger.info(f'Predicted clusters at: {output_eval_file}')

    docs = read_jsonlines(file=eval_file)
    with open(output_eval_file, "w") as writer:
        for doc in docs:
            doc_key = doc['doc_key']
            # assert doc_key in doc_to_prediction
            if doc_key in doc_to_prediction:

                predicted_clusters = doc_to_prediction[doc_key]
                tokens = doc_to_tokens[doc_key]
                subtoken_map = doc_to_subtoken_map[doc_key]
                new_word_map = doc_to_new_word_map[doc_key]

                new_predicted_clusters = align_clusters(predicted_clusters, subtoken_map, new_word_map)
                doc['tokens'] = tokens
                doc['clusters'] = new_predicted_clusters

                writer.write(json.dumps(doc) + "\n")


def to_dataframe(file_path):
    global nlp
    df = pd.read_json(file_path, lines=True)

    if 'tokens' in df.columns:
        pass
    elif 'sentences' in df.columns:
        # this is just for ontonotes. please avoid using 'sentences' and use 'text' or 'tokens'
        df['tokens'] = df['sentences'].apply(lambda x: flatten(x))
    elif 'text' in df.columns:
        if nlp is None:
            nlp = spacy.load("en_core_web_sm", exclude=["tagger", "parser", "lemmatizer", "ner", "textcat"])
        texts = df['text'].tolist()
        logger.info(f'Tokenize documents using Spacy...')
        df['tokens'] = [[tok.text for tok in doc] for doc in tqdm(nlp.pipe(texts), total=len(texts))]
    else:
        raise NotImplementedError(f'The jsonlines must include tokens/text/sentences attribute')

    if 'speakers' in df.columns:
        df['speakers'] = df['speakers'].apply(lambda x: flatten(x))
    else:
        df['speakers'] = df['tokens'].apply(lambda x: [None] * len(x))

    if 'doc_key' not in df.columns:
        raise NotImplementedError(f'The jsonlines must include doc_key, you can use uuid.uuid4().hex to generate.')

    if 'clusters' in df.columns:
        df = df[['doc_key', 'tokens', 'speakers', 'clusters']]
    else:
        df = df[['doc_key', 'tokens', 'speakers']]

    df = df.dropna()
    df = df.reset_index(drop=True)
    return df


def set_seed(args):
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)


def save_all(model, tokenizer, output_dir):
    logger.info(f"Saving model to {output_dir}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save a trained model, configuration and tokenizer using `save_pretrained()`.
    # They can then be reloaded using `from_pretrained()`
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)


def extract_clusters(gold_clusters):
    gold_clusters = [tuple(tuple(m) for m in cluster if NULL_ID_FOR_COREF not in m) for cluster in gold_clusters]
    gold_clusters = [cluster for cluster in gold_clusters if len(cluster) > 0]
    return gold_clusters


def extract_mentions_to_clusters(gold_clusters):
    mention_to_gold = {}
    for gc in gold_clusters:
        for mention in gc:
            mention_to_gold[mention] = gc
    return mention_to_gold


def update_metrics(metrics, span_starts, span_ends, gold_clusters, predicted_clusters):
    gold_clusters = extract_clusters(gold_clusters)
    candidate_mentions = list(zip(span_starts, span_ends))

    mention_to_gold_clusters = extract_mentions_to_clusters(gold_clusters)
    mention_to_predicted_clusters = extract_mentions_to_clusters(predicted_clusters)

    gold_mentions = list(mention_to_gold_clusters.keys())
    predicted_mentions = list(mention_to_predicted_clusters.keys())

    metrics['post_pruning'].update(candidate_mentions, gold_mentions)
    metrics['mentions'].update(predicted_mentions, gold_mentions)
    metrics['coref'].update(predicted_clusters, gold_clusters,
                            mention_to_predicted_clusters, mention_to_gold_clusters)


def create_clusters(mention_to_antecedent):
    # Note: mention_to_antecedent is a numpy array

    clusters, mention_to_cluster = [], {}
    for mention, antecedent in mention_to_antecedent:
        mention, antecedent = tuple(mention), tuple(antecedent)
        if antecedent in mention_to_cluster:
            cluster_idx = mention_to_cluster[antecedent]
            if mention not in clusters[cluster_idx]:
                clusters[cluster_idx].append(mention)
                mention_to_cluster[mention] = cluster_idx
        elif mention in mention_to_cluster:
            cluster_idx = mention_to_cluster[mention]
            if antecedent not in clusters[cluster_idx]:
                clusters[cluster_idx].append(antecedent)
                mention_to_cluster[antecedent] = cluster_idx
        else:
            cluster_idx = len(clusters)
            mention_to_cluster[mention] = cluster_idx
            mention_to_cluster[antecedent] = cluster_idx
            clusters.append([antecedent, mention])

    clusters = [tuple(cluster) for cluster in clusters]
    return clusters

def update_cluster_with_singleton(pred_clusters, mentions):
    # Note: mentions is a numpy array
    # print(pred_clusters)
    mentions = tuple(mentions)
    all_non_singleton_mention = []
    all_singleton_mention = []
    
    for clu in pred_clusters:
        for men in clu:
            # Convert numpy array to tuple for comparison
            all_non_singleton_mention.append(tuple(men))
    
    for men in mentions:
        # Convert numpy array to tuple for comparison
        if tuple(men) not in all_non_singleton_mention:
            all_singleton_mention.append(tuple(men))
    
    # print(all_singleton_mention)
    # adding singletons
    # for men in all_singleton_mention:
    #     pred_clusters.append(tuple([men]))

    # print(pred_clusters)
    return pred_clusters

def vaild_mention(mention, subtoken_map):
    start, end = mention
    same_condition = subtoken_map[start] == subtoken_map[end]
    prev_condition = start == 0 or subtoken_map[start - 1] != subtoken_map[start]
    next_condition = end == len(subtoken_map) - 1 or subtoken_map[end + 1] != subtoken_map[end]
    if same_condition and prev_condition and next_condition:
        return True
    else:
        return False

def get_vaild_mention_to_antecedent(mention_to_antecedent, subtoken_map):
    vaild_mention_to_antecedent = []
    for link in mention_to_antecedent:
        men, ant = link
        if vaild_mention(men, subtoken_map) and vaild_mention(ant, subtoken_map):
            vaild_mention_to_antecedent.append(link)
        # else:
        #     print("invaild - ", link)
    return vaild_mention_to_antecedent

def create_mentions(span_starts, span_ends, men_logits, coref_logits):
    batch_size, n_spans, _ = men_logits.shape

    # max_antecedents = coref_logits.argmax(axis=-1)
    prob = np.max(coref_logits, axis=-1)
    avg_prob = np.average(prob, axis=1)
    avg_prob[avg_prob < 0] = 0
    avg_prob = avg_prob / 2

    # print("avg")
    # print(avg_prob)
    # print(avg_prob.shape)

    men_logits = np.diagonal(men_logits, axis1=1, axis2=2) / 2
    doc_indices, mention_indices = np.nonzero(men_logits < n_spans) 
    # Step 1: Ensure A has the same shape as axis 0 of B
    avg_prob = avg_prob.reshape(-1, 1)  # Reshape A to (5, 1) for broadcasting

    # Step 2: Create a boolean mask where B values are greater than or equal to A
    mask = men_logits >= avg_prob
    # Step 3: Use the mask to filter B
    filtered_men_logits = np.where(mask, men_logits, np.nan)  # Replace values that don't meet the criteria with NaN

    doc_indices, mention_indices = np.nonzero(filtered_men_logits < n_spans)        
    # print(doc_indices.shape, mention_indices.shape)
    # print(doc_indices)

    span_indices = np.stack([span_starts, span_ends], axis=-1)
    mentions = span_indices[doc_indices, mention_indices]
    
    return doc_indices, mentions

def create_mention_to_antecedent22(span_starts, span_ends, coref_logits):
    batch_size, n_spans, _ = coref_logits.shape

    max_antecedents = coref_logits.argmax(axis=-1)
    prob = coref_logits.max(axis=-1)
    avg_prob = np.average(prob, axis=1)
    # avg_prob = prob.average(axis=-1)
    print(prob.shape)
    print(avg_prob)
    print(avg_prob.shape)
    # with open("example_mention_Antecedent_test.txt", 'w') as f:
    #     f.write(max_antecedents)
    print(span_starts)
    np.savetxt("example_mention_Antecedent_test.txt", max_antecedents[0])
    print(max_antecedents)
    print("hello - ",max_antecedents.shape)
    print(max_antecedents[0])
    print(max_antecedents[0].shape)
    print(n_spans)
    doc_indices, mention_indices = np.nonzero(max_antecedents == n_spans)
    print(mention_indices)
    print("shape - ",mention_indices.shape)
    print(np.nonzero(max_antecedents < n_spans))
    doc_indices, mention_indices = np.nonzero(max_antecedents < n_spans)        # indices where antecedent is not null.
    print("shape - ",mention_indices.shape)
    antecedent_indices = max_antecedents[max_antecedents < n_spans]
    span_indices = np.stack([span_starts, span_ends], axis=-1)
    np.savetxt("example_mention_Antecedent_test_5.txt", span_indices[0])
    print("shape - ",antecedent_indices.shape)
    # np.savetxt("example_mention_Antecedent_test_2.txt", span_indices)

    mentions = span_indices[doc_indices, mention_indices]
    antecedents = span_indices[doc_indices, antecedent_indices]
    mention_to_antecedent = np.stack([mentions, antecedents], axis=1)
    print(mention_to_antecedent)
    np.savetxt("example_mention_Antecedent_test_3.txt", mention_to_antecedent[0])

    return doc_indices, mention_to_antecedent

def create_mention_to_antecedent(span_starts, span_ends, coref_logits):
    batch_size, n_spans, _ = coref_logits.shape

    max_antecedents = coref_logits.argmax(axis=-1)
    doc_indices, mention_indices = np.nonzero(max_antecedents < n_spans)        # indices where antecedent is not null.
    antecedent_indices = max_antecedents[max_antecedents < n_spans]
    span_indices = np.stack([span_starts, span_ends], axis=-1)

    mentions = span_indices[doc_indices, mention_indices]
    antecedents = span_indices[doc_indices, antecedent_indices]
    mention_to_antecedent = np.stack([mentions, antecedents], axis=1)

    return doc_indices, mention_to_antecedent

def pad_clusters_inside(clusters, max_cluster_size):
    return [cluster + [(NULL_ID_FOR_COREF, NULL_ID_FOR_COREF)] * (max_cluster_size - len(cluster)) for cluster
            in clusters]


def pad_clusters_outside(clusters, max_num_clusters):
    return clusters + [[]] * (max_num_clusters - len(clusters))


def pad_clusters(clusters, max_num_clusters, max_cluster_size):
    clusters = pad_clusters_outside(clusters, max_num_clusters)
    clusters = pad_clusters_inside(clusters, max_cluster_size)
    return clusters


def mask_tensor(t, mask):
    t = t + ((1.0 - mask.float()) * -10000.0)
    t = torch.clamp(t, min=-10000.0, max=10000.0)
    return t


def get_pronoun_id(span):
    # if len(span) == 1:
    #     span = list(span)
    #     if span[0] in PRONOUNS_GROUPS:
    #         return PRONOUNS_GROUPS[span[0]]
    return -1


# def check_if_contain_category(mentions, antecedents):
#     # print(mentions, antecedents)
#     if len(mentions) > len(antecedents):
#         for antecedent in antecedents:
#             if antecedent not in STOPWORDS and len(antecedent) > 3:
#                 is_found = False
#                 for mention in mentions:
#                     if are_words_similar(mention, antecedent):
#                         is_found = True
#                         break
#                 if not is_found:
#                     return False
#     else:
#         for mention in mentions:
#             if mention not in STOPWORDS and len(mention) > 3:
#                 is_found = False
#                 for antecedent in antecedents:
#                     if are_words_similar(mention, antecedent):
#                         is_found = True
#                         break
#                 if not is_found:
#                     return False
#     return True
#     # union = mentions.union(antecedents)
#     # return len(union) == max(len(mentions), len(antecedents))

# def check_if_contain_category_2(mentions, antecedents):
#     mention = mentions[-1]
#     antecedent = antecedents[-1]
#     if mention in antecedent or antecedent in mention:
#         return True
#     return False

def get_category_id(mention, antecedent):
    
    mention, mention_pronoun_id = mention
    antecedent, antecedent_pronoun_id = antecedent
    
    if len(mention) == 0 or len(antecedent) == 0 or len(mention) > 1 or len(antecedent) > 1:
        # print(mention , antecedent)
        return CATEGORIES['invalid']
    
    mention , antecedent = mention[0] , antecedent[0]
    
    if mention == antecedent:
        return CATEGORIES['token_match']
    elif mention in antecedent or antecedent in mention:
        return CATEGORIES['token_contain']
    # elif mention not in token_to_category_map or antecedent not in token_to_category_map:
    #     return CATEGORIES['other']
    # elif len(token_to_category_map[mention]) == 0 or len(token_to_category_map[antecedent]) == 0:
    #     return CATEGORIES['other']
    
    # mention_type = token_to_category_map[mention]
    # antecedent_type = token_to_category_map[antecedent]
    # union_type = mention_type.union(antecedent_type)

    # if mention_type == antecedent_type:
    #     return CATEGORIES['total_case_match']
    # elif len(union_type) == len(mention_type) or len(union_type) == len(antecedent_type):
    #     return CATEGORIES['total_case_match']
    # elif len(union_type) < len(mention_type) + len(antecedent_type):
    #     return CATEGORIES['partial_case_match']
    # else:
    #     return CATEGORIES['no_case_match']

    return check_men_comp(mention, antecedent)

def check_men_comp(men1, men2):
    
    if men1 not in token_to_category_map or men2 not in token_to_category_map: 
        # print("missing - ", men1, men2)
        return CATEGORIES['other']

    men1_type = token_to_category_map[men1]
    men2_type = token_to_category_map[men2]

    if len(men1_type) == 0 or len(men2_type) == 0: # or len(men1_g) == 0 or len(men2_g) == 0: 
        return CATEGORIES['other']
    
    union_type = men1_type.union(men2_type)
    inter_type = men1_type.intersection(men2_type)

    if len(union_type) == len(men1_type) or len(union_type) == len(men2_type):
        return CATEGORIES['total_case_match']
    elif len(union_type) < len(men1_type) + len(men2_type): # len(inter_type) > 0: # 
        return CATEGORIES['partial_case_match']
    else:
        return CATEGORIES['no_case_match']

def check_men_comp_gn(men1, men2):
    
    if men1 not in token_to_category_map_g or men1 not in token_to_category_map_n or men2 not in token_to_category_map_g or men2 not in token_to_category_map_n: 
        # print("missing - ", men1, men2)
        return CATEGORIES['invalid']

    men1_g, men1_n = token_to_category_map_g[men1], token_to_category_map_n[men1]
    men2_g, men2_n = token_to_category_map_g[men2], token_to_category_map_n[men2]

    if len(men1_n) == 0 or len(men2_n) == 0: # or len(men1_g) == 0 or len(men2_g) == 0: 
        return CATEGORIES['other']
    
    union_g = men1_g.union(men2_g)
    union_n = men1_n.union(men2_n)
    inter_g = men1_g.intersection(men2_g)
    inter_n = men1_n.intersection(men2_n)

    if len(men1_g) > 0 and len(men2_g) > 0 and (len(union_g) == len(men1_g) or len(union_g) == len(men2_g)) and (len(union_n) == len(men1_n) or len(union_n) == len(men2_n)):
        return CATEGORIES['total_case_match']
    elif ((len(men1_g) == 0 and len(men2_g) == 0) or len(inter_g) > 0) and len(inter_n) > 0:
        return CATEGORIES['partial_case_match']
    else:
        return CATEGORIES['no_case_match']

# 2 ending different group or same group 
# match
# contain
# other
