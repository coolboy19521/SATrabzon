import os
import csv
import random

OPT_SIZ = 4
ALT_CNT = 4
BIT_SIZ = 16
PNC_SYM = ',.:-'
SRC_DIR = 'sets'
PLC_HLD = '______'
OBY_PRF = ('ed', 'ing')
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

def generate_pin(included):
    pin = 0
    for package_index, set_index in included:
       pin |= 1 << (prefix_sum[package_index] + set_index)
    random.seed(os.urandom(BIT_SIZ))
    pin |= random.randint(0, 1 << BIT_SIZ) << prefix_sum[-1]
    return hex(pin)

def get_question(pin, index):
    pin = int(pin, BIT_SIZ)
    words = []
    package_index, set_index = 0, 0
    for i in range(prefix_sum[-1]):
        if i == prefix_sum[package_index + 1]:
            package_index, set_index = package_index + 1, 0
        if pin & 1 << i: words += all_words[package_index][set_index]
        set_index += 1
    question_type = index // ALT_CNT % 3
    random.seed((seed := pin >> prefix_sum[-1]) << index)
    chosen = random.randint(0, OPT_SIZ - 1)
    random.seed(seed)
    random.shuffle(words)
    while (index + 1) * OPT_SIZ >= len(words):
        random.shuffle(words)
        index -= len(words) // OPT_SIZ
    options = words[index * OPT_SIZ : (index + 1) * OPT_SIZ]
    match question_type:
        case 0: question = (options[chosen][2], *options, chosen, 0)
        case 1:
            statement = list(options[chosen][3].split())
            root = (options[chosen][1] + '(').lower()
            root = [word for word in root[:root.index('(')].split() if word not in OBY_WRD][0]
            is_lower, in_sentence = False, None
            for i, word in enumerate(statement):
                if word.lower().startswith(root):
                    statement[i] = PLC_HLD + (word[-1] if word[-1] in PNC_SYM else '')
                    is_lower, in_sentence = word.islower(), word[:-1] if word[-1] in PNC_SYM else word
            can_obey = in_sentence is None
            if not can_obey:
                for obey_word in OBY_PRF: can_obey = can_obey or in_sentence.endswith(obey_word)
            if can_obey:
                random.seed(seed << index)
                index = random.randint(0, 1 << BIT_SIZ)
                index = index // ALT_CNT * ALT_CNT
                index += (4 - (index // ALT_CNT % 3)) * ALT_CNT
                return get_question(hex(pin), index)
            options[chosen][1] = in_sentence
            if is_lower:
                for option in options: option[1] = option[1].lower()
            question = (' '.join(statement), *options, chosen, 1)
        case 2: question = (options[chosen][1], *options, chosen, 2)
    return question
