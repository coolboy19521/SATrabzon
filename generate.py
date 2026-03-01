import os
import csv
import copy
import random

QST_TYP = 3
OPT_SIZ = 4
ALT_CNT = 4
BIT_SIZ = 12
REP_SIZ = 16
ORG_CNS = 30
PNC_SYM = ',.:-'
SRC_DIR = 'sets'
PLC_HLD = '______'
PKG_FIL = 'packages.csv'
OBY_WRD = ('to', 'a', 'the', 'an')

with open(PKG_FIL, "r") as src:
    packages = list(csv.reader(src))

all_words = []
for package_name, package_size in packages:
    all_words.append([])
    for set_index in range(int(package_size)):
        with open(f"{SRC_DIR}/{package_name}/set-{set_index + 1}.csv", "r", encoding='latin-1') as src:
            all_words[-1].append([i for i in csv.reader(src) if len(i) != 0])

prefix_sum = [0 for _ in range(len(packages) + 1)]
for i in range(0, len(packages)):
    prefix_sum[i + 1] = prefix_sum[i] + int(packages[i][1])

def get_pin(included):
    pin = 0
    for package_index, set_index in included:
       pin |= 1 << (prefix_sum[package_index] + set_index)
    rng = random.Random(os.urandom(BIT_SIZ >> 3))
    pin |= rng.randint(0, 1 << BIT_SIZ) << prefix_sum[-1]
    return hex(pin)

def extract_example(search_word):
    statement = list(search_word[3].split())
    root = (search_word[1] + '(').lower()
    root = [word for word in root[:root.index('(')].split() if word not in OBY_WRD][0]
    is_lower, in_sentence = False, None
    for i, word in enumerate(statement):
        if word.lower().startswith(root):
            statement[i] = PLC_HLD + (word[-1] if word[-1] in PNC_SYM else '')
            is_lower, in_sentence = word.islower(), word[:-1] if word[-1] in PNC_SYM else word
    return statement, is_lower, in_sentence

def get_similarity(a, b):
    if a is None or b is None: return 0
    common_suffix = 0
    for i in range(1, min(len(a), len(b))):
        if a[-i] == b[-i]: common_suffix += 1
        else: break
    return common_suffix

def get_question(pin, index):
    pin = int(pin, REP_SIZ)
    words = []
    package_index, set_index = 0, 0
    for i in range(prefix_sum[-1]):
        if i == prefix_sum[package_index + 1]:
            package_index, set_index = package_index + 1, 0
        if pin & 1 << i: words += all_words[package_index][set_index]
        set_index += 1
    question_type = index // ALT_CNT % QST_TYP
    revolution_count = (index // len(words)) + 1
    seed = pin >> prefix_sum[-1]
    answer_rng = random.Random(seed << revolution_count << question_type)
    answer_rng.shuffle(words)
    local_index = index % len(words)
    ans = words[((local_index // ALT_CNT) // QST_TYP) * ALT_CNT + (local_index % ALT_CNT)]
    if question_type == 0:
        statement, is_lower, in_sentence = extract_example(ans)
        if in_sentence is not None:
            supplemental_words = []
            for word in words:
                if word != ans:
                    word_in_sentence = extract_example(word)[2]
                    similarity_word = get_similarity(word, in_sentence)
                    similarity_usage = get_similarity(word_in_sentence, in_sentence)
                    if similarity_word > similarity_usage and similarity_word > 0:
                        for _ in range(similarity_word): supplemental_words.append(word)
                    elif similarity_usage > 0:
                        words.remove(word)
                        new_word = word.copy()
                        new_word[1] = word_in_sentence.capitalize()
                        for _ in range(similarity_usage + 1): supplemental_words.append(new_word)
            for word in supplemental_words: words.append(word)
    word_revolution = OPT_SIZ * index // len(words)
    shuffle_rng = random.Random(seed << word_revolution)
    shuffle_rng.shuffle(words)
    option_index = (OPT_SIZ * index) % len(words)
    words = words + words[:OPT_SIZ]
    options = [ans.copy()]
    for i in range(option_index, len(words)):
        if len(options) >= OPT_SIZ: break
        if words[i] not in options: options.append(words[i].copy())
    choice_rng = random.Random(seed << index)
    answer_index = choice_rng.randint(0, OPT_SIZ - 1)
    options[0], options[answer_index] = options[answer_index], options[0]
    match question_type:
        case 0:
            if in_sentence is None:
                big_half = (1 << (BIT_SIZ - 1))
                ix = choice_rng.randint(big_half, 2 * big_half) * QST_TYP * ALT_CNT
                return get_question(hex(pin), ix)
            options[answer_index][1] = in_sentence
            if is_lower:
                for option in options: option[1] = option[1].lower()
            question = (' '.join(statement), *options, answer_index, 0)
        case 1: question = (options[answer_index][2], *options, answer_index, 1)
        case 2: question = (options[answer_index][1], *options, answer_index, 2)
    return question