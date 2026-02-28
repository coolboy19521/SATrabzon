import os
import csv

def save(words):
    os.makedirs(f"{DST_DIR}/{packages[package_index][0]}", exist_ok = True)
    with open(f"{DST_DIR}/{packages[package_index][0]}/set-{set_index + 1}.csv", "w") as dest:
        writer = csv.writer(dest)
        writer.writerows(words)

SRC_DIR = 'data'
DST_DIR = 'sets'
PKG_FIL = 'packages.csv'

with open(PKG_FIL, "r") as src:
    packages = list(csv.reader(src))

files = sorted(os.listdir(SRC_DIR), key = lambda x: int(x.split('-')[2]))

words = []
set_index = 0
last_index = 0
package_index = 0

trans_table = str.maketrans("—“”’", "-'''")

for file in files:
    with open(f'{SRC_DIR}/{file}', encoding='utf-8') as src:
        for word in csv.reader(src):
            sterile = []
            for part in word:
                if part != "": sterile.append(part.translate(trans_table))
            if len(sterile) == 0 or sterile[0] == '#': continue
            if not sterile[0].isnumeric() and sterile[0][0].isnumeric():
                sterile = [sterile[0].split()[0]] + [' '.join(sterile[0].split()[1:])] + sterile[1:]
            if sterile[0].isnumeric():
                new_index = int(sterile[0])
                if new_index < last_index:
                    save(words), words.clear()
                    last_index, set_index = 0, set_index + 1
                    if set_index == int(packages[package_index][1]):
                        set_index = 0
                        package_index += 1
                        if package_index == len(packages): exit()
                last_index = new_index
            words.append(sterile)