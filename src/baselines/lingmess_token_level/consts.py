SUPPORTED_MODELS = ['longformer', 'roberta', 'bert']
SPEAKER_START = '#####'
SPEAKER_END = '###'
NULL_ID_FOR_COREF = -1


# PRONOUNS_GROUPS = {
#             'i': 0, 'me': 0, 'my': 0, 'mine': 0, 'myself': 0,
#             'you': 1, 'your': 1, 'yours': 1, 'yourself': 1, 'yourselves': 1,
#             'he': 2, 'him': 2, 'his': 2, 'himself': 2,
#             'she': 3, 'her': 3, 'hers': 3, 'herself': 3,
#             'it': 4, 'its': 4, 'itself': 4,
#             'we': 5, 'us': 5, 'our': 5, 'ours': 5, 'ourselves': 5,
#             'they': 6, 'them': 6, 'their': 6, 'themselves': 6,
#             'that': 7, 'this': 7
# }
PRONOUNS_GROUPS = {}

# STOPWORDS = {"'s", 'a', 'all', 'an', 'and', 'at', 'for', 'from', 'in', 'into',
#              'more', 'of', 'on', 'or', 'some', 'the', 'these', 'those'}
STOPWORDS = {
    'aTaH', 'aTa', 'api', 'ayam', 'arTa', 'apitu', 'anya', 'api', 'atra', 'aDuna',
    'iti', 'itTaM', 'eva', 'kadAcit', 'kiM', 'kaTaM', 'kasmAt', 'kadA', 'kasmin', 'kaTaMcit',
    'cit', 'tatra', 'taTaH', 'taTApi', 'taTA', 'taDa', 'tasmAt', 'tasmin', 'tu', 'te', 'dRuStvA',
    'punaH', 'punarapi', 'pUrva', 'param', 'paScAt', 'pratyuta', 'yaTA', 'yadi', 'yadRcCayA', 'yatra',
    'yadA', 'yAvat', 'saH', 'sA', 'tad', 'sarva', 'samprati', 'saha', 'hi', 'hyaH'
}


CATEGORIES = {
            #   'pron-pron-comp': 0,
            #   'pron-pron-no-comp': 1,
              'no_case_match': 0,
              'token_match': 1,
              'token_contain': 2,
              'total_case_match': 3,
              'partial_case_match': 4,
              'other': 5,
              'invalid' : 6,
              }

