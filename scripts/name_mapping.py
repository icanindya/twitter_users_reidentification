import unidecode
import collections

db_path = r'D:\Data\Linkage\FL\FL18\name_processing\name_dictionary.txt'
db_path_2 = r'D:\Data\Linkage\FL\FL18\name_processing\name_dictionary_2.txt'
output_path = r'D:\Data\Linkage\FL\FL18\name_processing\name_mapping.txt'

longs_dict = collections.defaultdict(set)

with open(db_path, 'r', encoding='utf-8') as rf:

    for line in rf:

        line =  unidecode.unidecode(line)

        tokens = line.lower().split('=')

        if len(tokens) != 2:

            print(line)

        short = tokens[0].strip()

        longs = [token.strip() for token in tokens[1:]]

        longs_dict[short].update(longs)


with open(db_path_2, 'r', encoding='utf-8') as rf:

    for line in rf:

        line =  unidecode.unidecode(line)

        parts = line.lower().split('-')

        long = parts[0].strip()

        shorts = [short.strip() for short in parts[1].split(',')]

        for short in shorts:

            longs_dict[short].add(long)

print(len(longs_dict))

with open(output_path, 'w', encoding='utf-8') as wf:

    for key in sorted(longs_dict.keys()):

        values = sorted(list(longs_dict[key]))

        wf.write('{}: {}\n'.format(key, ','.join(values)))







