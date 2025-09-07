
def get_not_singleton(input_list):
    return [sublist for sublist in input_list if len(sublist) > 1]

def sandhi_mention(input_list):
    men_list = []
    sandhi_mention_list = []
    for clu in input_list:
        for men in clu:
            if men in men_list and men not in sandhi_mention_list:
                sandhi_mention_list.append(men)
            men_list.append(men)
    return sandhi_mention_list

def sandhi_cluster(input_clutser_list, input_mention_list):
    sandhi_cluster_list = []
    for clu in input_clutser_list:
        # if len(clu) > 1:
            for men in clu:
                if men in input_mention_list:
                    sandhi_cluster_list.append(clu)
                    break
    return sandhi_cluster_list

def remove_dup_mention_in_cluster(input_list):
    new_list = []
    for clu in input_list:
        new_clu = []
        for men in clu:
            if men not in new_clu:
                new_clu.append(men)
        new_list.append(new_clu)
    return new_list

def main(gold_clusters, pred_clusters):
    
    sandhi_mention_gold_count = 0
    sandhi_mention_pred_count = 0
    sandhi_cluster_gold_count = 0
    sandhi_cluster_pred_count = 0
    sandhi_mention_gold_without_singleton_count = 0
    sandhi_mention_pred_without_singleton_count = 0
    sandhi_cluster_gold_without_singleton_count = 0
    sandhi_cluster_pred_without_singleton_count = 0
    valid_case_gold_count = 0 
    valid_case_pred_count = 0 
    valid_case_gold_without_singleton_count = 0 
    valid_case_pred_without_singleton_count = 0 

    for gold_cluster, pred_cluster in zip(gold_clusters, pred_clusters):

        gold_cluster = remove_dup_mention_in_cluster(gold_cluster)
        pred_cluster = remove_dup_mention_in_cluster(pred_cluster)

        # Get sandhi mentions
        sandhi_mention_gold = sandhi_mention(gold_cluster)
        sandhi_mention_pred = sandhi_mention(pred_cluster)

        if len(sandhi_mention_gold) > 0:
            valid_case_gold_count += 1
        if len(sandhi_mention_pred) > 0:
            valid_case_pred_count += 1

        # Get sandhi clusters
        sandhi_cluster_gold = sandhi_cluster(gold_cluster, sandhi_mention_gold)
        sandhi_cluster_pred = sandhi_cluster(pred_cluster, sandhi_mention_pred)

        sandhi_mention_gold_count += len(sandhi_mention_gold)
        sandhi_mention_pred_count += len(sandhi_mention_pred)
        sandhi_cluster_gold_count += len(sandhi_cluster_gold)
        sandhi_cluster_pred_count += len(sandhi_cluster_pred)

        gold_cluster_without_singleton = get_not_singleton(gold_cluster)
        pred_cluster_without_singleton = get_not_singleton(pred_cluster)

        sandhi_mention_gold_without_singleton = sandhi_mention(gold_cluster_without_singleton)
        sandhi_mention_pred_without_singleton = sandhi_mention(pred_cluster_without_singleton)

        if len(sandhi_mention_gold_without_singleton) > 0:
            valid_case_gold_without_singleton_count += 1
        if len(sandhi_mention_pred_without_singleton) > 0:
            valid_case_pred_without_singleton_count += 1

        sandhi_cluster_gold_without_singleton = sandhi_cluster(gold_cluster_without_singleton, sandhi_mention_gold_without_singleton)
        sandhi_cluster_pred_without_singleton = sandhi_cluster(pred_cluster_without_singleton, sandhi_mention_pred_without_singleton)

        sandhi_mention_gold_without_singleton_count += len(sandhi_mention_gold_without_singleton)
        sandhi_mention_pred_without_singleton_count += len(sandhi_mention_pred_without_singleton)
        sandhi_cluster_gold_without_singleton_count += len(sandhi_cluster_gold_without_singleton)
        sandhi_cluster_pred_without_singleton_count += len(sandhi_cluster_pred_without_singleton)

        # print(sandhi_mention_gold_count, sandhi_cluster_gold_count)
        # if len(sandhi_mention_gold) == len(sandhi_cluster_gold):
        #     print(sandhi_mention_gold)
        #     print(sandhi_cluster_gold)
        #     print()
            # break
        # print(sandhi_mention_gold_without_singleton_count, sandhi_cluster_gold_without_singleton_count)
        # if sandhi_mention_gold_without_singleton_count < sandhi_cluster_gold_without_singleton_count:
        #     print(sandhi_mention_gold_without_singleton)
        #     print(sandhi_cluster_gold_without_singleton)
        #     break
    
    # Print counts
    print("(unique mentions that has sandhi) sandhi_mention_gold_count:", sandhi_mention_gold_count)
    print("(unique mentions that has sandhi) sandhi_mention_pred_count:", sandhi_mention_pred_count)
    print("(number of different cluster that has at least 1 sandhi mention) sandhi_cluster_gold_count:", sandhi_cluster_gold_count)
    print("(number of different cluster that has at least 1 sandhi mention) sandhi_cluster_pred_count:", sandhi_cluster_pred_count)
    print("(unique mentions that has sandhi) sandhi_mention_gold_without_singleton_count:", sandhi_mention_gold_without_singleton_count)
    print("(unique mentions that has sandhi) sandhi_mention_pred_without_singleton_count:", sandhi_mention_pred_without_singleton_count)
    print("(number of different cluster that has at least 1 sandhi mention) sandhi_cluster_gold_without_singleton_count:", sandhi_cluster_gold_without_singleton_count)
    print("(number of different cluster that has at least 1 sandhi mention) sandhi_cluster_pred_without_singleton_count:", sandhi_cluster_pred_without_singleton_count)
    
    # Print percentages
    if len(gold_clusters) > 0:
        print("Number of doc has sandhi in gold:", (valid_case_gold_count / len(gold_clusters)) * 100, "%")
        print("Number of doc has sandhi in gold without singletons:", (valid_case_gold_without_singleton_count / len(gold_clusters)) * 100, "%")
    if len(pred_clusters) > 0:
        print("Number of doc has sandhi in pred:", (valid_case_pred_count / len(pred_clusters)) * 100, "%")
        print("Number of doc has sandhi in pred without singletons:", (valid_case_pred_without_singleton_count / len(pred_clusters)) * 100, "%")
    if sandhi_mention_gold_count > 0:
        print("Ratio of sandhi mentions in gold without singletons / total (with or without singleton):", (sandhi_mention_gold_without_singleton_count / sandhi_mention_gold_count) * 100, "%")
    if sandhi_mention_pred_count > 0:
        print("Ratio of sandhi mentions in pred without singletons / total (with or without singleton):", (sandhi_mention_pred_without_singleton_count / sandhi_mention_pred_count) * 100, "%")
    if sandhi_cluster_gold_count > 0:
        print("Ratio of sandhi clusters in gold without singletons / total (with or without singleton):", (sandhi_cluster_gold_without_singleton_count / sandhi_cluster_gold_count) * 100, "%")
    if sandhi_cluster_pred_count > 0:
        print("Ratio of sandhi clusters in pred without singletons / total (with or without singleton):", (sandhi_cluster_pred_without_singleton_count / sandhi_cluster_pred_count) * 100, "%")


if __name__ == "__main__":
    # Example usage
    gold_clusters = [[[[0, 0]], [[6, 6], [68, 68], [75, 75], [208, 208]], [[10, 10], [26, 26]], [[13, 13]], [[18, 18], [154, 154]], [[35, 35], [57, 57], [135, 135], [217, 217]], [[39, 39], [55, 55]], [[81, 81]], [[159, 159], [182, 182]], [[162, 162], [191, 191]], [[171, 171]], [[222, 222]]]]
    pred_clusters = [[[[10, 10], [26, 26]], [[39, 39], [55, 55]], [[6, 6], [68, 68], [75, 75], [208, 208]], [[57, 57], [135, 135], [217, 217]], [[18, 18], [154, 154]], [[159, 159], [182, 182]], [[162, 162], [191, 191]]]]

    main(gold_clusters, pred_clusters)


# 
# [[488, 488]]
# [[[488, 488]], [[488, 488]]]

# [[98, 98]]
# [[[4, 4], [52, 52], [64, 64], [98, 98]], [[98, 98]]]

# [[11, 11]]
# [[[11, 11], [16, 16], [49, 49], [64, 64]], [[11, 11], [15, 15], [24, 24], [38, 38], [98, 98]]]

# [[191, 191]]
# [[[191, 191]], [[191, 191]]]

# [[20, 20]]
# [[[20, 20], [101, 101], [204, 204]], [[20, 20], [29, 29], [37, 37], [65, 65], [214, 214]]]