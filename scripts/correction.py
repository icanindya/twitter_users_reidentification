import pandas as pd
import json
import csv

onegram_path = r'D:\maif_1grams_label.txt'
twogram_path = r'D:\maif_2grams_label.txt'

maif_input_col_names = ['twitter_id', 'doc', 'dob_or_age']

for input_ds_path in [onegram_path, twogram_path]:

    with open(input_ds_path + '.new', 'w', newline='', encoding='utf-8') as wf_csv:
        writer = csv.writer(wf_csv, delimiter=',')

        df = pd.read_csv(input_ds_path, encoding='utf-8', names=maif_input_col_names)
        # df = data.loc[:, maif_input_col_names]

        for i, row in df.iterrows():
            twitter_id = str(row['twitter_id'])
            doc = row['doc']
            dob_or_age = row['dob_or_age']
            print(dob_or_age)
            j = json.loads(dob_or_age)
            age = json.loads(dob_or_age)['age']

            writer.writerow([twitter_id, doc, age])



