import get_homonames_doc
import get_homonames_doc_chapter
import os

def flatten(input_list):
    return [item for sublist in input_list for item in sublist]

def evaluate_clusters(pred_homo_cluster, homoname_dict):
    total_doc = len(pred_homo_cluster)
    total_clu = 0
    total_correct_clu = 0
    total_conflated_clu = 0
    total_divided_clu = 0
    total_missing_clu = 0
    total_correct_pred = 0
    total_partial_pred = 0
    total_false_pred = 0

    type_count = {"correct":0, "conflated":0, "divided":0, "missing":0}  
    mention_count = {"missing":0, "extra":0}

    for key, pred_cluster in pred_homo_cluster.items():
        homoname_cluster = homoname_dict[key][1]

        for homoname in homoname_cluster:
            all_men = flatten(homoname)
            all_clu = len(homoname)
            total_clu += all_clu
            correct_clu = 0
            partial_correct_clu = 0
            merged_clu = 0
            false_clu = 0

            conflated_clu = 0
            divided_clu = 0
            missing_clu = 0

            all_pred_men = flatten(pred_cluster)

            for men in all_men:
                if men not in all_pred_men:
                    mention_count["missing"] += 1

            clu_type_count = {"correct":0, "partial_correct":0, "conflated":0, "divided":0, "missing":0} 
            for clu in homoname:
                rest_men = [men for men in all_men if men not in clu]
                # print("range - ", len(clu))

                for clu2 in pred_cluster:
                    if all(men not in rest_men for men in clu2) and all(men in clu2 for men in clu):
                        clu_type_count["correct"] += 1
                        break
                    elif all(men in clu2 for men in all_men):
                        clu_type_count["conflated"] = all_clu 
                        break
                    elif all(men not in rest_men for men in clu2) and any(men in clu2 for men in clu):
                        clu_type_count["divided"] += 1
                    elif any(men in rest_men for men in clu2) and all(men in clu2 for men in clu):
                        # clu_type_count["partial_correct"] += 1
                        clu_type_count["conflated"] += 2
                        break

            rem_clu = len(homoname)
            correct_pred, conflated_pred, divided_pred, partial_correct_pred, missing_pred = 0, 0, 0, 0 ,0
            if clu_type_count["correct"] > 0:
                correct_pred = clu_type_count["correct"] / all_clu if all_clu else 0
                total_correct_clu += clu_type_count["correct"]
                rem_clu -= clu_type_count["correct"]
            
            if clu_type_count["conflated"] > 0 and rem_clu > 0:
                clu_type_count["conflated"] = min(rem_clu, clu_type_count["conflated"])
                conflated_pred = clu_type_count["conflated"] / all_clu if all_clu else 0
                total_conflated_clu += clu_type_count["conflated"]
                rem_clu -= clu_type_count["conflated"]

            min_merged_divided =0 
            # if clu_type_count["partial_correct"] > 0 and rem_clu > 0:
            #     min_merged_divided = min(clu_type_count["partial_correct"], clu_type_count["divided"], rem_clu)
            #     partial_correct_pred = min_merged_divided / all_clu if all_clu else 0
            #     total_divided_clu += min_merged_divided
            #     total_conflated_clu += min_merged_divided
            #     rem_clu -= min_merged_divided
            #     clu_type_count["divided"] -= min_merged_divided
            #     clu_type_count["partial_correct"] -= min_merged_divided
            
            if clu_type_count["partial_correct"] > 0 and rem_clu > 0:
                clu_type_count["partial_correct"] = min(clu_type_count["partial_correct"], rem_clu)
                partial_correct_pred = clu_type_count["partial_correct"] / all_clu if all_clu else 0
                total_conflated_clu += clu_type_count["partial_correct"]
                rem_clu -= clu_type_count["partial_correct"]

            if clu_type_count["divided"] > 0 and rem_clu > 0:
                clu_type_count["divided"] = min(clu_type_count["divided"], rem_clu)
                divided_pred = clu_type_count["divided"] / all_clu if all_clu else 0
                total_divided_clu += clu_type_count["divided"]
                rem_clu -= clu_type_count["divided"]
            
            # clu_type_count["divided"] += min_merged_divided 
            # clu_type_count["conflated"] += min_merged_divided 

            if rem_clu > 0:
                missing_pred = rem_clu / all_clu if all_clu else 0
                total_missing_clu += rem_clu
            
            # print(correct_pred, conflated_pred, divided_pred, partial_correct_pred, missing_pred)
            print(f'Correct: {clu_type_count["correct"]} / {all_clu}, conflated: {clu_type_count["conflated"]}, divided: {clu_type_count["divided"]}, missing: {rem_clu}')
            # print(total_correct_clu, total_divided_clu, total_conflated_clu, total_missing_clu)

    print(f'Total Documents: {total_doc}')
    print(f'Total Clusters: {total_clu}')
    print(f'Total Correct Clusters: {total_correct_clu}')
    print(f'Total divided Clusters: {total_divided_clu}')
    print(f'Total conflated Clusters: {total_conflated_clu}')
    print(f'Total missing Clusters: {total_missing_clu}')
    print("mention count - ")
    print(mention_count)

    # return (total_doc, total_clu, total_correct_clu, total_partial_correct_clu, total_merged_clu, total_false_clu,
    #         total_correct_clu / total_clu if total_doc else 0, 
    #         total_partial_correct_clu / total_clu if total_clu else 0, 
    #         total_merged_clu * 2 / total_clu if total_clu else 0, 
    #         total_false_clu  / total_clu if total_clu else 0)

def main(pred_doc_keys, pred_clusters, is_chapter = False):
    if is_chapter:
        homoname_dict = get_homonames_doc_chapter.main('./')
    else:
        homoname_dict = get_homonames_doc.main('./')
    homoname_dict = {os.path.basename(key): value for key, value in homoname_dict.items()}
    homoname_doc_keys = list(homoname_dict.keys())
    pred_doc_keys = [file_name[:-2] if file_name.endswith('_0') else file_name for file_name in pred_doc_keys]

    pred_homo_cluster = {doc_key: pred_cluster for doc_key, pred_cluster in zip(pred_doc_keys, pred_clusters) if doc_key in homoname_doc_keys}

    # print("Predicted Homo Cluster:")
    # for key, value in pred_homo_cluster.items():
    #     print(f'{key}: {value}')
    evaluate_clusters(pred_homo_cluster, homoname_dict)
    
if __name__ == "__main__":
    # Example usage
    # main(gold_clusters, pred_clusters)
    print("please provide clusters")
