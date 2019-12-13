import os

import numpy as np
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr

LEXICON_DATA_DIR = r'D:\Data\Linkage\FL\FL18\trinker-lexicon-4c5e22b\data'
LEXICON_DATA_TXT_DIR = r'D:\Data\Linkage\FL\FL18\trinker-lexicon-4c5e22b\data_txt'
if not os.path.exists(LEXICON_DATA_TXT_DIR):
    os.mkdir(LEXICON_DATA_TXT_DIR)

for rda_file_name in os.listdir(LEXICON_DATA_DIR):

    rda_file_path = os.path.join(LEXICON_DATA_DIR, rda_file_name)
    txt_file_path = os.path.join(LEXICON_DATA_TXT_DIR, rda_file_name[:-3] + 'txt')

    if os.path.isfile(rda_file_path):
        pandas2ri.activate()
        base = importr('base')
        base.rm(list=base.ls())
        base.load(rda_file_path)
        rdf_List = base.mget(base.ls())

        pydf_dict = {}

        for i, f in enumerate(base.names(rdf_List)):
            pydf_dict[f] = pandas2ri.ri2py_vector(rdf_List[i])

        for k, v in pydf_dict.items():

            print(type(v), rda_file_name)

            with open(txt_file_path, 'w') as wf:

                if (isinstance(v, np.recarray)):
                    for item in v:
                        wf.write(','.join(([str(elem) for elem in item])) + '\n')
                elif (isinstance(v, np.ndarray)):
                    for item in v:
                        wf.write(str(item) + '\n')
                else:
                    print('error')

        pandas2ri.deactivate()
