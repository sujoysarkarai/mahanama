# def build_entity_index(pem_filename: str, output_path: str):
#     pem = load_pem(pem_filename)
#     all_qcodes: Set[str] = set()
#     for qcode_probs in tqdm(pem.values()):
#         all_qcodes.update(set(qcode_probs.keys()))
#     qcode_to_index = {qcode: qcode_idx + 1 for qcode_idx, qcode in enumerate(list(all_qcodes))}

#     with open(os.path.join(output_path, 'qcode_to_idx.json.part'), 'w') as fout:
#         for k, v in qcode_to_index.items():
#             fout.write(json.dumps({'qcode': k, 'index': v}) + '\n')
#     os.rename(os.path.join(output_path, 'qcode_to_idx.json.part'), os.path.join(output_path, 'qcode_to_idx.json'))

# OUTPUT_PATH = 'data'
# if not os.path.exists(os.path.join(OUTPUT_PATH, 'qcode_to_idx.json')):
#     build_entity_index(os.path.join(OUTPUT_PATH, 'wiki_pem.json'), OUTPUT_PATH)