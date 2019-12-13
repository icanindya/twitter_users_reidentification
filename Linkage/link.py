import pandas as pd
import recordlinkage as rl
import numpy as np
import random

LINKAGE_DSB = r'D:\Data\Linkage\FL\FL18\linkage\linkage_dsb_agegrouped.csv'
LINKAGE_DSB_DIST = r'D:\Data\Linkage\FL\FL18\linkage\linkage_dsb_agegrouped_dist.txt'
attributes = ['gender', 'yob', 'race', 'party']

# dfb = pd.read_csv(LINKAGE_DSB, header=0, index_col=None)
# series = dfb.groupby(attributes).index.nunique()
# with open(LINKAGE_DSB_DIST, 'w') as wf:
#     for i, v in series.items():
#         wf.write('{}\t{}\n'.format(i, v))

freq_list = []
indv_acc_list = []
samp_acc_list = []

with open(LINKAGE_DSB_DIST, 'r') as rf:
    for line in rf:
        tokens = line.strip().split('\t')
        indv_acc_list.append(1/int(tokens[1]))
        freq_list.append(int(tokens[1]))

print(sum(freq_list))

for i in range(100):
    samp_indv_acc = random.sample(indv_acc_list, k=100)
    samp_acc = sum(samp_indv_acc)/len(samp_indv_acc)
    samp_acc_list.append(samp_acc)
    print(samp_acc)
acc = sum(samp_acc_list)/len(samp_acc_list)

print(acc)

# dfa = dfb.sample(n=100, random_state=0)
# indexer = rl.index.Block(left_on=attributes, right_on=attributes)
# candidate_links = indexer.index(dfa, dfb)
# print(candidate_links)
# compare_cl = rl.Compare()
# for att in attributes:
#     compare_cl.exact(att, att, label=att)
# features = compare_cl.compute(candidate_links, dfa, dfb)



# ecm = rl.ECMClassifier()
# result_ecm = ecm.fit_predict(features)
# rl.confusion_matrix(krebs_true_links, result_ecm, len(krebs_X))
# rl.fscore(krebs_true_links, result_ecm)


# print(features[:3])
