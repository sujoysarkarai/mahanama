import json
import analysis_mention_detection
import analysis_sandhi_cluster
import analysis_homoname_cluster
import analysis_entity_detection

def get_cluster(lines, type = "gold"):
    json_lines = [json.loads(line) for line in lines]
    if type == "pred":
        cluster_lines = [line["predicted_clusters"] for line in json_lines]
    else:
        cluster_lines = [line["clusters"] for line in json_lines]
    return cluster_lines

def get_subtoken_map(lines):
    json_lines = [json.loads(line) for line in lines]
    subtoken_map_lines = [line["subtoken_map"] for line in json_lines]
    return subtoken_map_lines

def get_doc_key(lines):
    json_lines = [json.loads(line) for line in lines]
    doc_key_lines = [line["doc_key"] for line in json_lines]
    return doc_key_lines

def get_clusters_strings(lines):
    json_lines = [json.loads(line) for line in lines]
    clusters_strings_lines = [line["clusters_strings"] for line in json_lines]
    return clusters_strings_lines

def get_cluster_heads(lines):
    json_lines = [json.loads(line) for line in lines]
    cluster_heads_lines = [line["cluster_heads"] for line in json_lines]
    return cluster_heads_lines

def get_filler_from_pred(gold_lines, pred_lines):
    pred_list = get_doc_key(pred_lines)
    fillered_gold_lines = [ line for line in gold_lines if json.loads(line)['doc_key'] in pred_list]
    return fillered_gold_lines

def subtoken_to_token_level(clusters, subtoken_map):
    token_map = dict()
    for idx in range(len(subtoken_map)):
        token_map[idx] = subtoken_map[idx]
    
    new_clusters = []
    for clu in clusters:
        new_clu = []
        for men in clu:
            new_clu.append( [token_map[men[0]], token_map[men[1]]])
        new_clusters.append(new_clu)
        
    return new_clusters


def main(gold_file, pred_file):
    # Read the JSON lines file
    with open(gold_file, 'r', encoding='utf-8') as f:
        gold_lines = f.readlines()

    with open(pred_file, 'r', encoding='utf-8') as f:
        pred_lines = f.readlines()

    gold_lines = get_filler_from_pred(gold_lines, pred_lines)
    gold_cluster = get_cluster(gold_lines, "gold")
    pred_cluster = get_cluster(pred_lines, "pred")
    pred_subtoken_map = get_subtoken_map(pred_lines)
    gold_clusters_strings = get_clusters_strings(gold_lines)
    gold_cluster_heads = get_cluster_heads(gold_lines)

    # for clu in gold_cluster[49:50]:
    #     print(clu)
    
    # for clu in pred_cluster[40:50]:
    #     print(clu)

    token_pred_cluster = []
    for clu, subtoken_map in zip(pred_cluster, pred_subtoken_map):
        token_pred_cluster.append(subtoken_to_token_level(clu, subtoken_map))

    # analysis_mention_detection.main(gold_cluster, pred_cluster)
    # print(len(gold_lines))
    # idx = 1
    # print(len(gold_cluster[idx]))
    # print(len(pred_cluster[idx]))
    # print(pred_cluster[idx])
    # # print(gold_clusters_strings[0][0])
    # # print(gold_cluster_heads[0][0])
    # exit()
    analysis_entity_detection.main(gold_cluster, pred_cluster, gold_clusters_strings, gold_cluster_heads)
    # analysis_sandhi_cluster.main(gold_cluster, pred_cluster)
    # analysis_homoname_cluster.main(get_doc_key(pred_lines), token_pred_cluster, is_chapter = False)
    # analysis_homoname_cluster.main(get_doc_key(pred_lines), token_pred_cluster, is_chapter = True)

if __name__ == "__main__":
    main('./test_info.4096.jsonlines', './test.log.jsonl')
    # main('./test_chapter_info.4096.jsonlines', './test_chapter.log.jsonl')
