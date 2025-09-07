from collections import Counter
import analysis_entity_spread_error

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

def main(clusters_map):
    print("Spread (First and last mention) -")
    analysis_entity_spread_error.predict_spread(clusters_map)
    analysis_entity_spread_error.predict_lexcial_variation(clusters_map)
    analysis_entity_spread_error.mutitoken_multimention(clusters_map)

if __name__ == "__main__":
    # Example usage
    main([[[[[0, 0], [17, 17]], [[[0, 0], [17, 17]]], 'correct'], [[[5, 5], [18, 18], [115, 115], [134, 134], [212, 212], [214, 214]], [[[5, 5], [18, 18], [115, 115], [134, 134], [212, 212], [214, 214]]], 'correct'], [[[15, 15]], [], 'missing'], [[[46, 46], [67, 67], [85, 85], [163, 163], [233, 233], [257, 257]], [], 'missing']]])
    print("please provide your cluster map")
