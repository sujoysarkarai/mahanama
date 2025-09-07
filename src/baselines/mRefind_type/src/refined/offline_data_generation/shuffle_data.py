import json
import random
import os

def shuffle_jsonl_with_priority(input_file, titles_file, output_file):
    try:
        # Read the priority titles from the titles file
        with open(titles_file, 'r', encoding='utf-8') as file:
            priority_titles = set(line.strip() for line in file if line.strip())

        # Read the JSONL file and parse each line as a JSON object
        with open(input_file, 'r', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]
        
        # Separate entries into priority and non-priority lists
        priority_titles = [os.path.basename(entry) for entry in priority_titles]
        # print(len(priority_titles))
        
        priority_entries = [entry for entry in data if entry.get("title") in priority_titles]
        non_priority_entries = [entry for entry in data if entry.get("title") not in priority_titles]

        # Shuffle both lists
        random.shuffle(priority_entries)
        random.shuffle(non_priority_entries)

        # Combine the lists, with priority entries appearing first
        shuffled_data = priority_entries + non_priority_entries

        # Write the shuffled data back to a new JSONL file
        with open(output_file, 'w', encoding='utf-8') as file:
            for entry in shuffled_data:
                file.write(json.dumps(entry, ensure_ascii=False) + '\n')

        print(f"Shuffled lines have been saved to {output_file}.")

    except json.JSONDecodeError:
        print("Error: One or more lines in the input file are not valid JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
input_file = 'data/output.json'   # Replace with your input file path
titles_file = '../final_data/conll_format/test_file_list_v2.txt'  # Replace with your titles file path
output_file = 'data/wikipedia_links_aligned_spans.json'  # Replace with your desired output file path
shuffle_jsonl_with_priority(input_file, titles_file, output_file)
