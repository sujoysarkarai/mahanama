from sanskit_utils import call_files_s_code

def build_cluster_id_to_qcode_sanskit():
    # folder_path = "../../../../../final_data/conll_format/v3"
    folder_path = "../final_data/conll_format/v3_devnagari"
    s_qcode, qcode = call_files_s_code(folder_path)
    cluster_id_to_qcode = dict()
    for i, key in enumerate(qcode):
        cluster_id_to_qcode[key] = "Q" + str(key.replace('_0', ''))
        
    for i, key in enumerate(s_qcode.keys()):
        if "1176_1"==key:
            cluster_id_to_qcode[key] = "Q11763"
            continue
        cluster_id_to_qcode[key] = "Q" + str(key.split("_")[0] + key.split("_")[1])

    # print(len(s_qcode) + len(qcode))
    # print(len(s_qcode))
    # print(len(qcode))
    # print(len(set(cluster_id_to_qcode.keys())))
    # print(len(set(cluster_id_to_qcode.values())))
    # 11761_0 1176_1
    # 1176_1 -> 11763
    # exit()
    
    return cluster_id_to_qcode