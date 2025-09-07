def flatten(input_list):
    return [item for sublist in input_list for item in sublist]

def get_singleton(input_list):
    return set(tuple(sublist[0]) for sublist in input_list if len(sublist) == 1)

def main(gold_clusters, pred_clusters):
    
    in_gold_not_in_pred_count = 0
    not_in_gold_in_pred_count = 0
    in_gold_not_in_pred_wo_single_count = 0
    not_in_gold_in_pred_wo_single_count = 0
    all_gold_mention_count = 0
    all_pred_mention_count = 0
    all_gold_mention_without_singleton_count = 0
    all_pred_mention_without_singleton_count = 0
    all_gold_singleton_count = 0
    all_pred_singleton_count = 0

    for gold_cluster, pred_cluster in zip(gold_clusters, pred_clusters):

        # Get singletons
        singleton_gold_mention = get_singleton(gold_cluster)
        singleton_pred_mention = get_singleton(pred_cluster)

        all_gold_singleton_count += len(singleton_gold_mention)
        all_pred_singleton_count += len(singleton_pred_mention)

        # Flatten the clusters
        all_gold_mention = flatten(gold_cluster)
        all_pred_mention = flatten(pred_cluster)

        # Convert mentions to tuples (if they are lists) to make them hashable
        all_gold_mention = set(tuple(men) if isinstance(men, list) else men for men in all_gold_mention)
        all_pred_mention = set(tuple(men) if isinstance(men, list) else men for men in all_pred_mention)

        all_gold_mention_count += len(all_gold_mention)
        all_pred_mention_count += len(all_pred_mention)

        # Find mentions in gold not in pred
        in_gold_not_in_pred = [men for men in all_gold_mention if men not in all_pred_mention]

        # Find mentions in pred not in gold
        not_in_gold_in_pred = [men for men in all_pred_mention if men not in all_gold_mention]

        in_gold_not_in_pred_count += len(in_gold_not_in_pred)
        not_in_gold_in_pred_count += len(not_in_gold_in_pred)

        # Find mentions in gold not in pred without singletons
        in_gold_not_in_pred_wo_single = set(men for men in in_gold_not_in_pred if men not in singleton_gold_mention)
        not_in_gold_in_pred_wo_single = set(men for men in not_in_gold_in_pred if men not in singleton_gold_mention)
        
        in_gold_not_in_pred_wo_single_count += len(in_gold_not_in_pred_wo_single)
        not_in_gold_in_pred_wo_single_count += len(not_in_gold_in_pred_wo_single)

        # Find all mentions without singletons
        all_gold_mention_single_wo = set(men for men in all_gold_mention if men not in singleton_gold_mention)
        all_pred_mention_single_wo = set(men for men in all_pred_mention if men not in singleton_gold_mention)
        
        all_gold_mention_without_singleton_count += len(all_gold_mention_single_wo)
        all_pred_mention_without_singleton_count += len(all_pred_mention_single_wo)
    
    # Print counts
    print("in_gold_not_in_pred_count:", in_gold_not_in_pred_count)
    print("not_in_gold_in_pred_count:", not_in_gold_in_pred_count)
    print("in_gold_not_in_pred_wo_single_count:", in_gold_not_in_pred_wo_single_count)
    print("not_in_gold_in_pred_wo_single_count:", not_in_gold_in_pred_wo_single_count)
    print("all_gold_mention_count:", all_gold_mention_count)
    print("all_pred_mention_count:", all_pred_mention_count)
    print("all_gold_mention_without_singleton_count:", all_gold_mention_without_singleton_count)
    print("all_pred_mention_without_singleton_count:", all_pred_mention_without_singleton_count)
    print("all_gold_singleton_count:", all_gold_singleton_count)
    print("all_pred_singleton_count:", all_pred_singleton_count)
    
    # Print percentages
    if all_gold_mention_count > 0:
        print("Percentage in gold not in pred:", (in_gold_not_in_pred_count / all_gold_mention_count) * 100)
    if all_pred_mention_count > 0:
        print("Percentage not in gold in pred:", (not_in_gold_in_pred_count / all_pred_mention_count) * 100)
    if all_gold_mention_count > 0:
        print("Percentage of singletons in gold:", (all_gold_singleton_count /  all_gold_mention_count) * 100)
    if all_pred_mention_count > 0:
        print("Percentage of singletons in pred:", (all_pred_singleton_count / all_pred_mention_count) * 100)
    if all_gold_mention_without_singleton_count > 0:
        print("Percentage in gold not in pred without singletons:", (in_gold_not_in_pred_wo_single_count / all_gold_mention_without_singleton_count) * 100)
    if all_pred_mention_without_singleton_count > 0:
        print("Percentage not in gold in pred without singletons:", (not_in_gold_in_pred_wo_single_count / all_pred_mention_without_singleton_count) * 100)


if __name__ == "__main__":
    # Example usage
    gold_clusters = [[[[0, 0]], [[6, 6], [68, 68], [75, 75], [208, 208]], [[10, 10], [26, 26]], [[13, 13]], [[18, 18], [154, 154]], [[35, 35], [57, 57], [135, 135], [217, 217]], [[39, 39], [55, 55]], [[81, 81]], [[159, 159], [182, 182]], [[162, 162], [191, 191]], [[171, 171]], [[222, 222]]]]
    pred_clusters = [[[[10, 10], [26, 26]], [[39, 39], [55, 55]], [[6, 6], [68, 68], [75, 75], [208, 208]], [[57, 57], [135, 135], [217, 217]], [[18, 18], [154, 154]], [[159, 159], [182, 182]], [[162, 162], [191, 191]]]]

    main(gold_clusters, pred_clusters)
