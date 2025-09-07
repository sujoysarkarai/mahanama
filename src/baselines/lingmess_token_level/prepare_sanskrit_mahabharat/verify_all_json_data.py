import json

def extract_word(tokens, indices):
    """Extracts and joins tokens based on given indices."""
    try:
        return "".join(tokens[i] for i in range(indices[0], indices[-1] + 1))
    except:
        print(len(tokens))
        print(indices)
        return "".join(tokens[i] for i in range(indices[0], indices[-1] + 1))

def verify_clusters(data):
    """Verifies if extracted words from token indices match expected cluster strings."""
    tokens = data["tokens"]
    clusters = data["clusters"]
    expected_strings = data["clusters_strings"]
    
    for cluster, expected in zip(clusters, expected_strings):
        extracted = [[extract_word(tokens, indices)] for indices in cluster]
        
        if extracted == expected:
            print(f"✅ Cluster {expected} is correctly marked.")
        else:
            print(f"❌ Mismatch in cluster. Expected: {expected}, Got: {extracted}")

# Process all JSON objects from the file
file_path = "file_with_clusters.jsonlines"

with open(file_path, "r", encoding="utf-8") as file:
    for line_num, line in enumerate(file, start=1):
        try:
            data = json.loads(line.strip())
            print(f"\n🔍 Verifying JSON object {line_num}:")
            verify_clusters(data)
        except json.JSONDecodeError as e:
            print(f"❌ Error in line {line_num}: {e}")
