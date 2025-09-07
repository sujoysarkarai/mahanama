from Levenshtein import distance

suffixes_dict = {
    "male": {
        'a': {
            'singular': ['H', 'm', 'nA', 'Aya', 'At', 'sya', 'e'], # 0
            'dual': ['O', 'O', 'ByAm', 'ByAm', 'ByAm', 'yoH', 'yoH'],
            'plural': ['AH', 'An', 'EH', 'eByaH', 'eByaH', 'AnAm', 'ezu']
        },
        'A': {
            'singular': ['H', 'm', 'yA', 'AyAH', 'yAH', 'yAm', 'yAm'],
            'dual': ['yO', 'yO', 'ByAm', 'ByAm', 'ByAm', 'yOH', 'yOH'],
            'plural': ['yAH', 'yAH', 'IBiH', 'IByaH', 'IByaH', 'InAm', 'Izu']
        },
        'i': {
            'singular': ['H', 'm', 'nA', 'e', 'EH', 'i', 'O'],
            'dual': ['yO', 'yO', 'ByAm', 'ByAm', 'ByAm', 'yOH', 'yOH'],
            'plural': ['yaH', 'yaH', 'iBiH', 'iByaH', 'iByaH', 'InAm', 'izu']
        },
        'u': {
            'singular': ['H', 'm', 'nA', 've', 'vOH', 'u', 'O'],
            'dual': ['vO', 'vO', 'ByAm', 'ByAm', 'ByAm', 'vOH', 'vOH'],
            'plural': ['vaH', 'vaH', 'uBiH', 'uByaH', 'uByaH', 'UnAm', 'uSu']
        },
        'M': {
            'singular': ['M', 'M', 'nA', 'ne', 'M', 'M', 'ni'],
            'dual': ['Mau', 'Mau', 'bhyAm', 'bhyAm', 'bhyAm', 'moH', 'moH'],
            'plural': ['MAnI', 'MAnI', 'bhiH', 'bhyaH', 'bhyaH', 'MAnAm', 'Su']
        },
        'H': {
            'singular': ['H', 'H', 'nA', 'ne', 'H', 'H', 'ni'],
            'dual': ['Hau', 'Hau', 'bhyAm', 'bhyAm', 'bhyAm', 'hoH', 'hoH'],
            'plural': ['HAnI', 'HAnI', 'bhiH', 'bhyaH', 'bhyaH', 'HAnAm', 'Su']
        },
        'niSi': {
            'singular': ['niSiH', 'niSiM', 'niSInA', 'niSe', 'niSiH', 'niSiH', 'niSi'],
            'dual': ['niSInI', 'niSInI', 'niSInibhyAm', 'niSInibhyAm', 'niSInibhyAm', 'niSiNoH', 'niSiNoH'],
            'plural': ['niSInI', 'niSInI', 'niSInibhiH', 'niSInibhyaH', 'niSInibhyaH', 'niSInInAm', 'niSInI']
        },
        'Ra': {
            'singular': ['RaH', 'RaM', 'RanA', 'Re', 'RaH', 'RaH', 'Ra'],
            'dual': ['Raau', 'Raau', 'RaByAm', 'RaByAm', 'RaByAm', 'RauH', 'RauH'],
            'plural': ['RaAH', 'RaAH', 'RaBiH', 'RaByaH', 'RaByaH', 'RaAnAm', 'RaSu']
        },
        'jam': {
            'singular': ['jam', 'jam', 'jAnA', 'jame', 'jam', 'jam', 'jami'],
            'dual': ['jau', 'jau', 'jAByAm', 'jAByAm', 'jAByAm', 'jamoH', 'jamoH'],
            'plural': ['jAmI', 'jAmI', 'jAbhiH', 'jAbhyaH', 'jAbhyaH', 'jAmAn', 'jAsu']
        },
        'ta': {
            'singular': ['taH', 'tam', 'tAnA', 'tave', 'taH', 'taH', 'ti'],
            'dual': ['tau', 'tau', 'tubhyAm', 'tubhyAm', 'tubhyAm', 'toH', 'toH'],
            'plural': ['tAH', 'tAH', 'tubhiH', 'tubhyaH', 'tubhyaH', 'tAnAm', 'tAsu']
        }
    },
    "female": {
        'A': {
            'singular': ['A', 'Am', 'ayA', 'AyE', 'AyAH', 'AyAH', 'AyAm'],
            'dual': ['e', 'e', 'AByAm', 'AByAm', 'AByAm', 'ayoH', 'ayoH'],
            'plural': ['AH', 'AH', 'ABiH', 'AByaH', 'AByaH', 'AnAm', 'Asu']
        },
        'i': {
            'singular': ['iH', 'im', 'yA', 'yai', 'yAH', 'yAH', 'yAm'],
            'dual': ['yau', 'yau', 'ibhyAm', 'ibhyAm', 'ibhyAm', 'yoH', 'yoH'],
            'plural': ['yaH', 'yaH', 'ibhiH', 'ibhyaH', 'ibhyaH', 'inAm', 'iSu']
        },
        'I': {
            'singular': ['I', 'Im', 'yA', 'yai', 'yAH', 'yAH', 'yAm'],
            'dual': ['Iu', 'Iu', 'IBhyaM', 'IBhyaM', 'IBhyaM', 'yoH', 'yoH'],
            'plural': ['IH', 'IH', 'IBiH', 'IByaH', 'IByaH', 'InAm', 'ISu']
        }
    },
    "neuter": {
        'a': {
            'singular': ['a', 'am', 'a', 'e', 'aH', 'aH', 'ni'],
            'dual': ['au', 'au', 'bhyAm', 'bhyAm', 'bhyAm', 'aH', 'aH'],
            'plural': ['AH', 'AH', 'bhiH', 'bhyaH', 'bhyaH', 'AnAm', 'Su']
        },
        'M': {
            'singular': ['M', 'M', 'nA', 'ne', 'H', 'H', 'ni'],
            'dual': ['nI', 'nI', 'bhyAm', 'bhyAm', 'bhyAm', 'noH', 'noH'],
            'plural': ['nAni', 'nAni', 'bhiH', 'bhyaH', 'bhyaH', 'nAm', 'Su']
        },
        'H': {
            'singular': ['H', 'H', 'nA', 'ne', 'H', 'H', 'ni'],
            'dual': ['nI', 'nI', 'bhyAm', 'bhyAm', 'bhyAm', 'noH', 'noH'],
            'plural': ['nAni', 'nAni', 'bhiH', 'bhyaH', 'bhyaH', 'nAm', 'Su']
        },
        'O': {
            'singular': ['O', 'O', 'nA', 'ne', 'OH', 'OH', 'ni'],
            'dual': ['nI', 'nI', 'bhyAm', 'bhyAm', 'bhyAm', 'noH', 'noH'],
            'plural': ['nAni', 'nAni', 'bhiH', 'bhyaH', 'bhyaH', 'nAm', 'Su']
        },
        'o': {
            'singular': ['o', 'o', 'nA', 'ne', 'OH', 'OH', 'ni'],
            'dual': ['nI', 'nI', 'bhyAm', 'bhyAm', 'bhyAm', 'noH', 'noH'],
            'plural': ['nAni', 'nAni', 'bhiH', 'bhyaH', 'bhyaH', 'nAm', 'Su']
        },
        'e': {
            'singular': ['e', 'e', 'nA', 'ne', 'eH', 'eH', 'ni'],
            'dual': ['nI', 'nI', 'bhyAm', 'bhyAm', 'bhyAm', 'noH', 'noH'],
            'plural': ['nAni', 'nAni', 'bhiH', 'bhyaH', 'bhyaH', 'nAm', 'Su']
        },
        'n': {
            'singular': ['n', 'n', 'nA', 'ne', 'nH', 'nH', 'ni'],
            'dual': ['nI', 'nI', 'bhyAm', 'bhyAm', 'bhyAm', 'noH', 'noH'],
            'plural': ['nAni', 'nAni', 'bhiH', 'bhyaH', 'bhyaH', 'nAm', 'Su']
        }
    }
}

def generate_forms(base_word, suffixes_dict):
    forms = []
    forms.append(base_word)
    found = 0
    # print(base_word)
    # Iterate through each gender category
    for gender in suffixes_dict:
        # Iterate through each suffix type for the current gender
        for suffix in suffixes_dict[gender]:
            # Generate forms for each case form in singular, dual, and plural
            if base_word.endswith(suffix):
                found = 1
                for case_type in ['singular', 'dual', 'plural']:
                    for form in suffixes_dict[gender][suffix][case_type]:
                        forms.append(f"{base_word}{form}")

    # if found == 0:
    #     print(base_word)
    
    return forms

def are_words_similar(word1, word2, max_mismatches = -1):
    """
    Check if one word is in another word, allowing for some mismatches.

    Parameters:
    word1 (str): The first word.
    word2 (str): The second word.
    max_mismatches (int): The maximum number of allowed mismatches.

    Returns:
    bool: True if the words are similar within the allowed mismatches, False otherwise.
    """
    if max_mismatches == -1:
        max_mismatches = int(0.2 * max(len(word1), len(word2)))
        max_mismatches = max(min(max_mismatches, 5), 2)
        # print(max_mismatches)
    # Compute the Levenshtein distance between the two words
    dist = distance(word1, word2)
    
    # Check if the distance is within the allowed threshold
    return dist <= max_mismatches

if __name__ == "__main__":
    print(generate_forms('rAma', suffixes_dict))
