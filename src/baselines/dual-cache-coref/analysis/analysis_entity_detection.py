from collections import Counter
import analysis_entity_error

corr = dict()
def flatten(input_list):
    return [item for sublist in input_list for item in sublist]

def get_not_singleton_cluster(input_list):
    # return set(tuple(sublist[0]) for sublist in input_list if len(sublist) == 1)
    count_s = 0
    new_list = []
    for clusters in input_list:
        not_singleton_clusters = [sublist for sublist in clusters if len(sublist) > 1]
        count_s += (len(clusters) - len(not_singleton_clusters))
        new_list.append(not_singleton_clusters)
    
    print("number of singleton cluster = ", count_s)
    return new_list

def predict(gold_clusters, pred_clusters, gold_clusters_str = [], gold_clusters_heads = []):
    
    gold_cluster_count = 0
    pred_cluster_count = 0
    total_correct_cluster = 0
    total_conflated_cluster = 0
    total_divided_cluster = 0
    total_missing_cluster = 0
    total_extra_cluster = 0
    cc = 0
    mention_count = {"missing":0, "extra":0}
    clusters_map = []

    for gold_cluster, pred_cluster, gold_cluster_str, gold_cluster_head in zip(gold_clusters[:], pred_clusters[:], gold_clusters_str[:], gold_clusters_heads[:]):

        # gold_cluster = get_not_singleton_cluster(gold_cluster)
        # pred_cluster = get_not_singleton_cluster(pred_cluster)
        gold_cluster_count += len(gold_cluster)
        pred_cluster_count += len(pred_cluster)

        gold_map = dict()
        pred_map = dict()

        for i in range(len(gold_cluster)):
            for men in gold_cluster[i]:
                if tuple(men) not in gold_map.keys():
                    gold_map[tuple(men)] = []
                if i not in gold_map[tuple(men)]:
                    gold_map[tuple(men)].append(i) 
                # if len(gold_map[tuple(men)]) > 1:
                    # print(cc)
        # cc += 1
        for i in range(len(pred_cluster)):
            for men in pred_cluster[i]:
                if tuple(men) not in pred_map.keys():
                    pred_map[tuple(men)] = []
                if i not in pred_map[tuple(men)]:
                    pred_map[tuple(men)].append(i)

        # Flatten the clusters
        all_gold_mention = flatten(gold_cluster)
        all_pred_mention = flatten(pred_cluster)
        all_mention = all_gold_mention.copy()
        all_mention.extend(all_pred_mention)
        all_mention = list(set([ tuple(men) for men in all_mention]))

        # for men in all_mention:
        #     print(men, end = '\t')
        #     if men in gold_map.keys():
        #         print(gold_map[men], end = '\t')
        #     else:
        #         print("", end = '\t')
        #     if men in pred_map.keys():
        #         print(pred_map[men], end = '\t')
        #     print()

        correct_cluster = 0
        conflated_cluster = 0
        divided_cluster = 0
        missing_cluster = 0
        extra_cluster = 0
        non_extra_cluster = set()
        cluster_map = []

        for i in range(len(gold_cluster)):
            is_correct = False
            is_conflated= False
            is_divided = False
            total_corr_pred_num = 0
            without_men = 0
            clu_map = []

            clu = gold_cluster[i]
            clu_str = gold_cluster_str[i]
            clu_head = gold_cluster_head[i]
            
            # print(f"{i} : " , end = "")
            count = Counter()
            for men in clu:
                if tuple(men) in pred_map.keys():
                    # print(f"{pred_map[tuple(men)]}, " , end = "")-
                    for num in pred_map[tuple(men)]:
                        count[num] += 1
                else:
                    without_men += 1 
            # print(count)
            corr_gold_num = len(clu) - without_men

            clu_divided_list = []
            for x in count.keys():
                non_extra_cluster.add(x)
                corr_pred_this_clu_num = 0
                corr_pred_rest_num = 0
                for men in pred_cluster[x]:
                    if men in clu:
                        corr_pred_this_clu_num += 1
                    elif tuple(men) in gold_map.keys():
                        corr_pred_rest_num += 1
                total_corr_pred_num += corr_pred_this_clu_num
                if corr_pred_this_clu_num != 0:
                    clu_divided_list.append(pred_cluster[x])
                corr_pred_all_clu_num = corr_pred_this_clu_num + corr_pred_rest_num
                if corr_gold_num == count[x]:
                    if corr_pred_all_clu_num == corr_gold_num:
                        is_correct = True
                        clu_map = [clu, [pred_cluster[x]], "correct", clu_str, clu_head]
                        break
                    elif corr_pred_all_clu_num > corr_gold_num:
                        is_conflated = True
                        clu_map = [clu, [pred_cluster[x]], "conflated", clu_str, clu_head]
                        break
                elif total_corr_pred_num == corr_gold_num:
                    is_divided = True

            if is_correct :
                correct_cluster += 1
            elif is_conflated :
                conflated_cluster += 1
            elif is_divided :
                clu_map = [clu, clu_divided_list, "divided", clu_str, clu_head]
                divided_cluster += 1
            else: 
                clu_map = [clu, [], "missing", clu_str, clu_head]
                missing_cluster += 1
                for _ in clu:
                    mention_count["missing"] += 1
            
            cluster_map.append(clu_map)
            
        for i in range(len(pred_cluster)):
            if i not in non_extra_cluster:
                extra_cluster += 1
                clu_map = [[], [pred_cluster[i]], "extra", [], []]
                cluster_map.append(clu_map)
                for _ in pred_cluster[i]:
                    mention_count["extra"] += 1

        total_correct_cluster += correct_cluster
        total_conflated_cluster += conflated_cluster
        total_divided_cluster += divided_cluster 
        total_missing_cluster += missing_cluster
        total_extra_cluster += extra_cluster
        clusters_map.append(cluster_map)

        # if cc not in corr.keys():
        #     corr[cc] = correct_cluster
        # else:
        #     if corr[cc] != correct_cluster:
        #         print(cc)
        #         print(f"{corr[cc]} - {correct_cluster}")
        cc+=1
            
        # break
    
    # Print counts
    print("gold_cluster_count = ", gold_cluster_count)
    print("pred_cluster_count = ", pred_cluster_count)
    print("total_correct_cluster = ", total_correct_cluster, " = ", (total_correct_cluster/gold_cluster_count), "%")
    print("total_conflated_cluster = ", total_conflated_cluster, " = ", (total_conflated_cluster/gold_cluster_count), "%")
    print("total_divided_cluster = ", total_divided_cluster, " = ", (total_divided_cluster/gold_cluster_count), "%")
    print("total_missing_cluster = ", total_missing_cluster, " = ", (total_missing_cluster/gold_cluster_count), "%")
    print("total_extra_cluster = ", total_extra_cluster)
    print("\nmention = ", mention_count)

    return clusters_map
    
def main(gold_clusters, pred_clusters, gold_clusters_str = [], gold_clusters_heads = []):
    print("with singleton cluster -")
    clusters_map = predict(gold_clusters, pred_clusters, gold_clusters_str, gold_clusters_heads)
    # analysis_entity_error.main(clusters_map)

    # gold_clusters_wo_single = get_not_singleton_cluster(gold_clusters)
    # pred_clusters_wo_single = get_not_singleton_cluster(pred_clusters)
    # gold_clusters_str_wo_single = get_not_singleton_cluster(gold_clusters_str)
    # gold_clusters_heads_wo_single = get_not_singleton_cluster(gold_clusters_heads)

    # print("without singleton cluster -")
    # clusters_map = predict(gold_clusters_wo_single, pred_clusters_wo_single, gold_clusters_str_wo_single, gold_clusters_heads_wo_single)
    # analysis_entity_error.main(clusters_map)

if __name__ == "__main__":
    # Example usage
    gold_clusters = [[[[0, 0]], [[6, 6], [68, 68], [75, 75], [208, 208]], [[10, 10], [26, 26]], [[13, 13]], [[18, 18], [154, 154]], [[35, 35], [57, 57], [135, 135], [217, 217]], [[39, 39], [55, 55]], [[81, 81]], [[159, 159], [182, 182]], [[162, 162], [191, 191]], [[171, 171]], [[222, 222]]]]
    pred_clusters = [[[[10, 10], [26, 26]], [[39, 39], [55, 55]], [[6, 6], [68, 68], [75, 75], [208, 208]], [[57, 57], [135, 135], [217, 217]], [[18, 18], [154, 154]], [[159, 159], [182, 182]], [[162, 162], [191, 191]]]]

    main(gold_clusters, pred_clusters)
