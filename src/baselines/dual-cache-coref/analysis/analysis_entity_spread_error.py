from collections import defaultdict
def predict_spread(clusters_map):

    type_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}  # [0, 0, 0, 0, 0]
    actual_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}
    mention_count = {"missing":0, "extra":0}
    for cluster_map in clusters_map:
        for clu_map in cluster_map:
            gold_cluster, pred_clusters, type_cluster, _, _ = clu_map
            actual_count[type_cluster] += 1
            
            if len(gold_cluster) == 0:
                type_count[type_cluster] +=1
                mention_count["extra"] += 1 if len(pred_clusters[0]) == 1 else 2 
                continue
            first_mem = gold_cluster[0]
            last_mem = gold_cluster[0]

            for gold_men in gold_cluster[1:]:
                ms, me = gold_men
                if ms < first_mem[0]:
                    first_mem = gold_men
                if me > last_mem[1]:
                    last_mem = gold_men
            
            correct = False
            done = False
            contains = False

            if len(pred_clusters) == 0:
                type_count["missing"] +=1
                mention_count["missing"] += 1 if len(gold_cluster) == 1 else 2  # main missing error
                continue
            if type_cluster != "divided":
                pred_clu = pred_clusters[0]
                if first_mem in pred_clu and last_mem in pred_clu:
                    contains = True
                else:
                    contains = False
                
                if len(pred_clu) == 0:
                    continue
                first_mem_pred = pred_clu[0]
                last_mem_pred = pred_clu[0]

                for pred_men in pred_clu[1:]:
                    ms, me = pred_men
                    if ms < first_mem_pred[0]:
                        first_mem_pred = pred_men
                    if me > last_mem_pred[1]:
                        last_mem_pred = pred_men
                
                if first_mem[0] == first_mem_pred[0] and last_mem[0] == last_mem_pred[0]:
                    correct = True

                if type_cluster == "conflated" and (not correct or not contains):
                    type_count["conflated"] += 1
                elif correct and contains:
                    type_count["correct"] += 1
                elif contains and not correct:
                    type_count["extra"] += 1
                    if first_mem[0] != first_mem_pred[0] and last_mem[0] != last_mem_pred[0]:
                        mention_count["extra"] += 2
                    else:
                        mention_count["extra"] += 1
                else:
                    type_count["missing"] += 1
                    if first_mem not in pred_clu and last_mem not in pred_clu:
                        mention_count["missing"] += 2
                    else:
                        mention_count["missing"] += 1
            else:
                contains1 = False
                contains_prev = False
                for pred_clu in pred_clusters:
                    if first_mem in pred_clu:
                        contains1 = True
                    else:
                        contains1 = False
                    if last_mem in pred_clu and contains1:
                        contains = True
                    else:
                        contains1 = True
                    if contains1 and contains_prev:
                        type_count["divided"] += 1
                        contains1 = False
                        break
                    elif contains1:
                        contains_prev = True
                        continue
                    
                    if len(pred_clu) == 0:
                        continue
                    first_mem_pred = pred_clu[0]
                    last_mem_pred = pred_clu[0]

                    for pred_men in pred_clu[1:]:
                        ms, me = pred_men
                        if ms < first_mem_pred[0]:
                            first_mem_pred = pred_men
                        if me > last_mem_pred[1]:
                            last_mem_pred = pred_men

                    if first_mem[0] == first_mem_pred[0] and last_mem[0] == last_mem_pred[0]:
                        type_count["correct"] += 1
                    else:
                        type_count["extra"] += 1
                        if first_mem[0] != first_mem_pred[0] and last_mem[0] != last_mem_pred[0]:
                            mention_count["extra"] += 2
                        else:
                            mention_count["extra"] += 1
                if contains1:
                    type_count["missing"] += 1
                    mention_count["missing"] += 1
                if not contains_prev and not contains1:
                    mention_count["missing"] += 2
        # print(type_count)
    
    print(f"final spread ({sum(type_count.values())})- ")
    print(type_count)
    print(f"actual ({sum(actual_count.values())})- ")
    print(actual_count)
    print(f"mention ({sum(mention_count.values())})- ")
    print(mention_count)

def get_sandhi_mention(input_list):
    men_list = []
    sandhi_mention_list = []
    for clu, _, _, _, _ in input_list:
        for men in clu:
            if men in men_list and men not in sandhi_mention_list:
                sandhi_mention_list.append(men)
            men_list.append(men)
    return sandhi_mention_list

def edit_distance(str1, str2):
    m = len(str1)
    n = len(str2)
    
    # Create a table to store results of subproblems
    dp = [[0 for x in range(n + 1)] for x in range(m + 1)]
    
    # Fill dp[][] in bottom up manner
    for i in range(m + 1):
        for j in range(n + 1):
            # If first string is empty, only option is to
            # insert all characters of second string
            if i == 0:
                dp[i][j] = j    # Min. operations = j
            
            # If second string is empty, only option is to
            # remove all characters of first string
            elif j == 0:
                dp[i][j] = i    # Min. operations = i
            
            # If last characters are the same, ignore the last character
            # and recur for the remaining substring
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            
            # If the last character is different, consider all possibilities
            # and find the minimum
            else:
                dp[i][j] = 1 + min(dp[i][j - 1],    # Insert
                                   dp[i - 1][j],    # Remove
                                   dp[i - 1][j - 1]) # Replace
    
    return dp[m][n]

def strip_vibhakti(word):
    # Define a list of common vibhakti suffixes (can be extended)
    vibhakti_suffixes = [
        "AH", "A", "E", "I", "O", "AM", "AS", "UM", "IM", "AN", "INA", "ANA", "NA", "MA", "RA", "TA", "NAH",
        "AHA", "AT", "ATI", "ANT", "VATI", "YAH", "KAM", "I", "E", "O", "AH", "A", "I", "U", "UM", "E", "O",
        "NA", "MI", "NIM", "VAM", "RA", "TA", "THA", "AH", "AN", "I", "U", "E", "O"
    ]
    
    # Strip known suffixes from the word
    for suffix in vibhakti_suffixes:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    
    return word

def is_inflection(men_str, curr_head, clu_head):
    # bibatsum, bibatsu, arjuna - Inflection
    # svetasvam, svetasva, arjuna - Inflection
    inter = len(set(men_str).intersection(clu_head))
    uni = len(set(men_str).union(clu_head))
    if men_str == clu_head:
        return True
    if strip_vibhakti(men_str) == clu_head :
        return True
    if len(men_str) < 4:
        return False
    if inter + 4 >= uni:
        return True
    if 3*len(curr_head) >= 2*len(men_str):
        if len(men_str) > 5 and men_str[:-3] in clu_head:
            return True
        elif len(men_str) <= 5 and men_str[:-1] in clu_head:
            return True
    return False

def get_lexical_variation_type(clu_map, multitoken_multimention_mention):
    gold_cluster, _, _, gold_clu_str, gold_clu_head = clu_map
    if len(gold_cluster) == 0:
        return [] 
    lex_list = []
    for men, men_str, men_head in zip(gold_cluster, gold_clu_str, gold_clu_head):
        clu_head, curr_head = men_head
        men_str = men_str[0]
        men_str, curr_head, clu_head = men_str.lower(), curr_head.lower(), clu_head.lower()

        if men in multitoken_multimention_mention:
            continue # we are not handling this cases
        elif is_inflection(men_str, curr_head, clu_head):
            lex_list.append([men, "Inflection"])
        elif curr_head == clu_head:
            lex_list.append([men, "Multiword"])
        else:
            lex_list.append([men, "Sysnonyms"])

        # with open("text.txt", "a") as f:
        #     f.write(f"{men_str}, {curr_head}, {clu_head} - {lex_list[-1][1]}")
        #     f.write("\n")
        
    return lex_list

def predict_lexcial_variation(clusters_map):
    Inflection_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}  # [0, 0, 0, 0, 0]
    Multiword_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}
    Sysnonyms_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}
    type_count = {"Inflection": Inflection_count, "Multiword": Multiword_count, "Sysnonyms": Sysnonyms_count}
    actual_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}
    Inflection_mention = {"missing":0, "extra":0}
    Multiword_mention = {"missing":0, "extra":0}
    Sysnonyms_mention = {"missing":0, "extra":0}
    mention_count = {"Inflection": Inflection_mention, "Multiword": Multiword_mention, "Sysnonyms": Sysnonyms_mention}
    mention_lex_count = {"Inflection": 0, "Multiword": 0, "Sysnonyms": 0}
    for cluster_map in clusters_map:
        multitoken_multimention_mention = get_sandhi_mention(cluster_map)
        conflated_gold = []
        conflated_pred = []

        for clu_map in cluster_map:
            gold_cluster, pred_clusters, type_cluster, gold_clu_str, gold_clu_head = clu_map
            lexical_variation_men = get_lexical_variation_type(clu_map, multitoken_multimention_mention)
            mention_lex = {"Inflection": [], "Multiword": [], "Sysnonyms": []}

            for men, type_lex in lexical_variation_men:
                mention_lex_count[type_lex] += 1
                mention_lex[type_lex].append(men)

            actual_count[type_cluster] += 1
            if type_cluster == "correct":
                for key in mention_lex:
                    type_count[key][type_cluster] += 1
                continue
            
            if type_cluster == "extra":
                continue

            if type_cluster == "missing":
                for key in mention_lex:
                    if len(mention_lex[key]) > 0:
                        type_count[key][type_cluster] += 1
                        mention_count[key]["missing"] += len(mention_lex[key])
                    else:
                        type_count[key]["correct"] += 1

              
            if type_cluster == "divided":
                # count = 0
                total_pred_men = []
                found_lex = {"Inflection": False, "Multiword": False, "Sysnonyms": False}
                found_missing = 0
                for clu in pred_clusters:
                    for men in clu:
                        for key in mention_lex:
                            if men in mention_lex[key]:
                                found_lex[key] = True
                                total_pred_men.append(men)
                for men in gold_cluster:
                    for key in mention_lex:
                        if men in mention_lex[key] and men not in total_pred_men:
                            mention_count[key]["missing"] += 1
                for key in found_lex:
                    if found_lex[key] == True:
                        type_count[key][type_cluster] += 1
                    else:
                        type_count[key]["correct"] += 1




                # count_each_pred = 0
                # count_each_gold = 0
                # for men in gold_cluster:
                #     if men in lexical_variation_men:
                #         count_each_gold += 1
                #         if men in total_pred_men:
                #             count_each_pred += 1
                
                # count = count_each_gold - count_each_pred
                # if count > 0:
                #     type_count["divided"] +=1
                # else:
                #     type_count["correct"] +=1
                # mention_count["missing"] += count

            if type_cluster == "conflated":
                continue
    
    
    print(f"final lexical variation {sum(value for subdict in type_count.values() for value in subdict.values())}- ")
    print(mention_lex_count)
    for key in type_count:
        print(f"{key} ({sum(type_count[key].values())}) - ")
        print(type_count[key])
    print(f"actual ({sum(actual_count.values())})- ")
    print(actual_count)
    print(f"mention ({sum(value for subdict in mention_count.values() for value in subdict.values())})- ")
    print(mention_count)

def flatten(input_list):
    return [item for sublist in input_list for item in sublist]

def mutitoken_multimention(clusters_map):
    type_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}  # [0, 0, 0, 0, 0]
    actual_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}
    mention_count = {"missing":0, "extra":0}
    ccc = 0
    for cluster_map in clusters_map:
        sandhi_mention = get_sandhi_mention(cluster_map)
        conflated_map = defaultdict(list)

        for clu_map in cluster_map:
            gold_cluster, pred_clusters, type_cluster, gold_clu_str, gold_clu_head = clu_map

            actual_count[type_cluster] += 1
            if type_cluster == "correct":
                for men in gold_cluster:
                    if men in sandhi_mention:
                        type_count[type_cluster] +=1
                        break
                continue
            
            if type_cluster == "extra":
                # type_count[type_cluster] +=1
                continue

            if type_cluster == "missing":
                count = 0
                for men in gold_cluster:
                    if men in sandhi_mention:
                        count += 1
                if count > 0:
                    type_count["missing"] +=1
                # else:
                #     type_count["correct"] +=1
                mention_count["missing"] += count
            
            if type_cluster == "divided":
                count = 0
                total_pred_men = []
                for clu in pred_clusters:
                    total_pred_men.extend(clu)

                count_each_pred = 0
                count_each_gold = 0
                for men in gold_cluster:
                    if men in sandhi_mention:
                        count_each_gold += 1
                        if men in total_pred_men:
                            count_each_pred += 1
                
                count = count_each_gold - count_each_pred
                mention_count["missing"] += count

            if type_cluster == "conflated":
                # pred_clusters[0] is 2d hash
                # conflated_map[pred_clusters[0]].append(gold_cluster)
                # print(sandhi_mention)
                # exit()
                conflated_map[tuple(map(tuple, pred_clusters[0]))].append(gold_cluster)
                # for men in gold_cluster:
                #     if men in sandhi_mention:
                #         type_count["conflated"] += 1
                #         break


        for pred in conflated_map.keys():
            gold = conflated_map[pred]
            conflated_count = len(gold)
            gold = flatten(gold)
            has_sandhi = False
            count = 0
            
            for men in gold:
                if men in sandhi_mention:
                    has_sandhi = True
                    if men not in pred:
                        count += 1
                        
            if has_sandhi:
                type_count["conflated"] += conflated_count 
                ccc+=1
            # else:
                
                # type_count["correct"] += conflated_count
            mention_count["missing"] += count
        # if ccc > 0:
        #     print(type_count["conflated"])
        #     print(type_count["correct"])
        #     print(mention_count["missing"])
        #     exit()
    
    print(f"final multitoken multimention ({sum(type_count.values())})- ")
    print(type_count)
    print(f"actual ({sum(actual_count.values())})- ")
    print(actual_count)
    print(f"mention ({sum(mention_count.values())})- ")
    print(mention_count)

def distance_nearest_antecedent(clusters_map):
    return
    type_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}  # [0, 0, 0, 0, 0]
    actual_count = {"correct":0, "conflated":0, "divided":0, "missing":0, "extra":0}
    mention_count = {"missing":0, "extra":0}
    for cluster_map in clusters_map:
        for clu_map in cluster_map:
            gold_cluster, pred_clusters, type_cluster, _, _ = clu_map
            actual_count[type_cluster] += 1
            
            if len(gold_cluster) == 0:
                type_count[type_cluster] +=1
                mention_count["extra"] += 1 if len(pred_clusters[0]) == 1 else 2 
                continue
            first_mem = gold_cluster[0]
            last_mem = gold_cluster[0]

            for gold_men in gold_cluster[1:]:
                ms, me = gold_men
                if ms < first_mem[0]:
                    first_mem = gold_men
                if me > last_mem[1]:
                    last_mem = gold_men
            
            correct = False
            done = False
            contains = False

            if len(pred_clusters) == 0:
                type_count["missing"] +=1
                mention_count["missing"] += 1 if len(gold_cluster) == 1 else 2  # main missing error
                continue
            if type_cluster != "divided":
                pred_clu = pred_clusters[0]
                if first_mem in pred_clu and last_mem in pred_clu:
                    contains = True
                else:
                    contains = False
                
                if len(pred_clu) == 0:
                    continue
                first_mem_pred = pred_clu[0]
                last_mem_pred = pred_clu[0]

                for pred_men in pred_clu[1:]:
                    ms, me = pred_men
                    if ms < first_mem_pred[0]:
                        first_mem_pred = pred_men
                    if me > last_mem_pred[1]:
                        last_mem_pred = pred_men
                
                if first_mem[0] == first_mem_pred[0] and last_mem[0] == last_mem_pred[0]:
                    correct = True

                if type_cluster == "conflated" and (not correct or not contains):
                    type_count["conflated"] += 1
                elif correct and contains:
                    type_count["correct"] += 1
                elif contains and not correct:
                    type_count["extra"] += 1
                    if first_mem[0] != first_mem_pred[0] and last_mem[0] != last_mem_pred[0]:
                        mention_count["extra"] += 2
                    else:
                        mention_count["extra"] += 1
                else:
                    type_count["missing"] += 1
                    if first_mem not in pred_clu and last_mem not in pred_clu:
                        mention_count["missing"] += 2
                    else:
                        mention_count["missing"] += 1
            else:
                contains1 = False
                contains_prev = False
                for pred_clu in pred_clusters:
                    if first_mem in pred_clu:
                        contains1 = True
                    else:
                        contains1 = False
                    if last_mem in pred_clu and contains1:
                        contains = True
                    else:
                        contains1 = True
                    if contains1 and contains_prev:
                        type_count["divided"] += 1
                        contains1 = False
                        break
                    elif contains1:
                        contains_prev = True
                        continue
                    
                    if len(pred_clu) == 0:
                        continue
                    first_mem_pred = pred_clu[0]
                    last_mem_pred = pred_clu[0]

                    for pred_men in pred_clu[1:]:
                        ms, me = pred_men
                        if ms < first_mem_pred[0]:
                            first_mem_pred = pred_men
                        if me > last_mem_pred[1]:
                            last_mem_pred = pred_men

                    if first_mem[0] == first_mem_pred[0] and last_mem[0] == last_mem_pred[0]:
                        type_count["correct"] += 1
                    else:
                        type_count["extra"] += 1
                        if first_mem[0] != first_mem_pred[0] and last_mem[0] != last_mem_pred[0]:
                            mention_count["extra"] += 2
                        else:
                            mention_count["extra"] += 1
                if contains1:
                    type_count["missing"] += 1
                    mention_count["missing"] += 1
                if not contains_prev and not contains1:
                    mention_count["missing"] += 2
        # print(type_count)
    
    print(f"final spread ({sum(type_count.values())})- ")
    print(type_count)
    print(f"actual ({sum(actual_count.values())})- ")
    print(actual_count)
    print(f"mention ({sum(mention_count.values())})- ")
    print(mention_count)



if __name__ == "__main__":
    # Example usage
    print("please provide your cluster map")