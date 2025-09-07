import os
import random
import glob
import csv
from tqdm import tqdm

def get_test_file_list(test_csv_file_path):
    # Initialize an empty list to store the file names
    file_names = []

    # Open and read the CSV file
    with open(test_csv_file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            # Assuming each row is in the format: ['filename']
            # Strip the square brackets and single quotes
            cleaned_row = [item.strip("[]'") for item in row]
            # Extend the file_names list with the cleaned row
            file_names.extend(cleaned_row)

    print(len(file_names))
    return file_names


def get_test_file_list_txt(test_txt_file_path = '../../final_data/conll_format/test_file_list_v2.txt'):
    # Initialize an empty list to store the base file names
    file_names = []

    # Open and read the .txt file
    with open(test_txt_file_path, mode='r') as file:
        lines = file.readlines()
        for line in lines:
            # Strip any surrounding whitespace (including newlines)
            cleaned_line = line.strip()
            # Extract the base filename
            base_name = os.path.basename(cleaned_line)
            # Add the base filename to the list
            file_names.append(base_name)

    return file_names

def split_files(file_list, test_list, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    # Ensure the ratios add up to 1.0
    assert train_ratio + val_ratio + test_ratio == 1.0, "Ratios must add up to 1.0"

    # Shuffle the lines randomly
    random.shuffle(file_list)

    assert train_ratio + val_ratio + test_ratio == 1.0, "Ratios must add up to 1.0"

    # Calculate the number of lines for each split
    total_lines = len(file_list)
    test_count = 1000 # int(total_lines * test_ratio)

    test_curr_count = 0
    test_files = []
    remaining_lines = []
    print(len(test_list))

    # Ensure all the test files are selected from the test_list
    for name in tqdm(file_list):
        file_name = os.path.basename(name)
        if test_curr_count < test_count and file_name in test_list:
            test_files.append(name)
            test_curr_count += 1
        else:
            remaining_lines.append(name)
    
    # Ensure remaining lines are also shuffled
    random.shuffle(remaining_lines)

    # Calculate the number of lines for train and val splits from remaining lines
    remaining_lines_count = len(remaining_lines)
    train_count = int(remaining_lines_count * (train_ratio / (train_ratio + val_ratio)))
    val_count = remaining_lines_count - train_count  # Ensuring no loss due to rounding

    # Split the remaining lines
    train_files = remaining_lines[:train_count]
    val_files = remaining_lines[train_count:]

    print(f"Data split, train - {len(train_files)}, val - {len(val_files)}, test - {len(test_files)}")

    return train_files, val_files, test_files

def write_to_file(file_list, output_path):
    with open(output_path, 'w') as outfile:
        for file_path in file_list:
            with open(file_path, 'r') as infile:
                file_name = os.path.basename(file_path)
                # print(file_path)
                outfile.write(f"#begin document ({file_name}); part 000\n")
                while True:
                    lines = infile.readlines(64)  # Read in chunks of 1KB
                    if not lines:
                        break
                    outfile.writelines(lines)
                outfile.write("#end document\n")
                outfile.flush()  # Explicitly flush to disk after writing each file


def main(input_folder, output_folder, test_csv_file_path):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    conll_files = glob.glob(os.path.join(input_folder, '**/*.txt'), recursive=True)
    print("number of files - ",len(conll_files))

    test_file_list = get_test_file_list_txt() # get_test_file_list(test_csv_file_path)
    
    train_files, dev_files, test_files = split_files(conll_files, test_file_list)

    write_to_file(train_files, os.path.join(output_folder, 'train.txt'))
    write_to_file(dev_files, os.path.join(output_folder, 'dev.txt'))
    write_to_file(test_files, os.path.join(output_folder, 'test.txt'))

if __name__ == "__main__":

    # main('../../final_data/conll_format/v3/', '../../coref_resources/data/sanskrit_mahabharat/conll', '../../final_data/conll_format/list_of_possible_test_subchapters.csv')
    main('../../final_data/conll_format/v3/', '../../coref_resources/data/sanskrit_slp_dual/conll', '../../final_data/conll_format/list_of_possible_test_subchapters.csv')
