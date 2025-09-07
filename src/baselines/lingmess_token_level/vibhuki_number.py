class TrieNode:
    def __init__(self):
        self.children = {}
        self.categories = None

class SuffixTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, suffix, categories):
        node = self.root
        # Insert suffix in reversed order
        for char in reversed(suffix):
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.categories = categories  # Store categories at the end of the suffix

    def search(self, word):
        node = self.root
        best_match = None
        # Traverse the word in reverse to match suffix
        for char in reversed(word):
            if char in node.children:
                node = node.children[char]
                if node.categories:  # Found a match
                    best_match = node.categories
            else:
                break
        return best_match if best_match else []

reverse_dict = {
    'aH': ['singdec_ma'],
    'a': ['singdec_ma', 'singdec_na'],
    'am': ['singdec_ma', 'singdec_na', 'singdec_na'],
    'ena': ['singdec_ma', 'singdec_na'],
    'Aya': ['singdec_ma', 'singdec_na'],
    'At': ['singdec_ma', 'singdec_na'],
    'asya': ['singdec_ma', 'singdec_na'],
    'e': ['singdec_ma', 'singdec_na', 'dualdec_na', 'dualdec_na', 'dualdec_na'],
    'O': ['dualdec_ma', 'dualdec_ma', 'dualdec_ma'],
    'AByAm': ['dualdec_ma', 'dualdec_ma', 'dualdec_ma', 'dualdec_na', 'dualdec_na', 'dualdec_na'],
    'ayoH': ['dualdec_ma', 'dualdec_ma', 'dualdec_na', 'dualdec_na'],
    'AH': ['plurdec_ma', 'plurdec_ma'],
    'An': ['plurdec_ma'],
    'EH': ['plurdec_ma', 'plurdec_na'],
    'eByaH': ['plurdec_ma', 'plurdec_ma'],
    'AnAm': ['plurdec_ma', 'plurdec_na'],
    'ezu': ['plurdec_ma', 'plurdec_na'],
    'Ani': ['plurdec_na', 'plurdec_na', 'plurdec_na'],
    'ebyaH': ['plurdec_na', 'plurdec_na']
}


# Initialize and populate the Trie
suffix_trie = SuffixTrie()
for suffix, categories in reverse_dict.items():
    suffix_trie.insert(suffix, categories)

# Function to find the best match using the Trie
def vibhuki_number_find_best_category(word):
    return suffix_trie.search(word)

# Example usage
# word = input("Enter a word to find its category: ")
# categories = find_best_category(word)
# print(f"The word '{word}' fits into the following categories: {categories}")
