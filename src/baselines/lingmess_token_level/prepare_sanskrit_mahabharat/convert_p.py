import json
from tqdm import tqdm
import pickle

SAVE_PATH = "token_to_category.jsonl"
SAVE_PATH_GN = "token_to_category_gn.jsonl"
pattern_set = set()

def save_data(data, path=SAVE_PATH):
    """Save data in JSONL format."""
    with open(path, "w", encoding="utf-8") as f:
        for k, v in data.items():
            json.dump({"token": k, "categories": list(v)}, f)
            f.write("\n")
    print(f"Data saved to {path}")

def load_data(path=SAVE_PATH):
    """Load data from JSONL file."""
    loaded_data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            loaded_data[entry["token"]] = set(entry["categories"])
    return loaded_data

def save_data_gn(data_g, data_n, path=SAVE_PATH_GN):
    """Save data in JSONL format."""
    with open(path, "w", encoding="utf-8") as f:
        for k in data_g.keys():
            json.dump({"token": k, "categories_g": list(data_g[k]), "categories_n": list(data_n[k])},f)
            f.write("\n")
    print(f"Data saved to {path}")

def load_data_gn(path=SAVE_PATH_GN):
    """Load data from JSONL file."""
    loaded_data_g, loaded_data_n = {}, {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            loaded_data_g[entry["token"]] = set(entry["categories_g"])
            loaded_data_n[entry["token"]] = set(entry["categories_n"])
    return loaded_data_g, loaded_data_n

def main():
    global pattern_set
    print("Getting SHR data")
    # with open("../final_data/mahabharata_tokens_analysis_version_2_032025_combined.pkl", "rb") as f:
    with open("../../final_data/mahabharata_tokens_analysis_version_2_032025_combined.pkl", "rb") as f:
        data = pickle.load(f)
    
    print(type(data))
    patterns = ["m. sg.", "f. sg.", "n. sg.", "m. du.", "f. du.", "n. du.", "m. pl.", "f. pl.", "n. pl."]
    # patterns = ["m. sg.", "f. sg.", "n. sg.", "m. du.", "f. du.", "n. du.", "m. pl.", "f. pl.", "n. pl.", "ac. sg.", "mo. sg.", "ps. sg.", "ac. du.", "mo. du.", "ps. du.", "ac. pl.", "mo. pl.", "ps. pl."]
    patterns_g = ["m.", "f.", "n."]
    patterns_n = ["sg.", "du.", "pl."]
    token_to_category = {}
    token_to_category_g, token_to_category_n = {}, {}

    no_shr_given = 0
    no_shr_given_g, no_shr_given_n = 0, 0
    i = 0
    for k, v in tqdm(data.items()):
        # if k == '' or k == ' ' or k == "'" or k == "." or k == "..":
        #     continue
        k = k.lower()
        if k[0] == "'":
            k_wo = k[1:]
        else:
            k_wo = k
        try:
            morph_data = [x['morph'] for x in v["analysis"].values()]
            # Flatten the list
            flattened_data = [item for sublist in morph_data for item in sublist]
            for x in flattened_data:
                pattern_set.add(x)

            matching_patterns = {pattern for pattern in patterns if any(pattern in entry for entry in flattened_data)}
            matching_patterns_g = {pattern for pattern in patterns_g if any(pattern in entry for entry in flattened_data)}
            matching_patterns_n = {pattern for pattern in patterns_n if any(pattern in entry for entry in flattened_data)}
            # existing_patterns = {p for p in patterns if v['t']['morph'].str.contains(p, regex=False).any()}
            token_to_category[k] = matching_patterns
            token_to_category_g[k] = matching_patterns_g
            token_to_category_n[k] = matching_patterns_n
            token_to_category[k_wo] = matching_patterns
            token_to_category_g[k_wo] = matching_patterns_g
            token_to_category_n[k_wo] = matching_patterns_n
            if len(matching_patterns) == 0:
                no_shr_given += 1
            if len(matching_patterns_g) == 0:
                no_shr_given_g += 1
            if len(matching_patterns_n) == 0:
                no_shr_given_n += 1
        except Exception:
            # print("key")
            # print(k)
            # print(v)
            # exit()
            no_shr_given += 1
            no_shr_given_g += 1
            no_shr_given_n += 1
            token_to_category[k] = set()
            token_to_category_g[k] = set()
            token_to_category_n[k] = set()
            token_to_category[k_wo] = set()
            token_to_category_g[k_wo] = set()
            token_to_category_n[k_wo] = set()

    print("No SHR given, such cases:", no_shr_given)
    print("No SHR given, such cases:", no_shr_given_g)
    print("No SHR given, such cases:", no_shr_given_n)

    # Save the processed data as JSONL
    save_data(token_to_category)
    save_data_gn(token_to_category_g, token_to_category_n)
    pattern_set = sorted(pattern_set)
    with open("pattern_set.txt", "w", encoding="utf-8") as f:
        for x in pattern_set:
            f.write(x)
            f.write("\n")

    return token_to_category

if __name__ == "__main__":
    token_to_category = main()

    # Load and verify
    loaded_data = load_data()
    print("Loaded data sample:", list(loaded_data.items())[:5])  # Print first 5 entries
