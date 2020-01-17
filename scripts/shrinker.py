import pandas as pd

df = pd.read_csv(r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_voterside.csv", header=0, usecols=['voter_serial', 'fname', 'mname', 'lname'], nrows=10000000)

df.to_csv(r"D:\Data\Linkage\FL\FL18\linkage\linkage_dataset_voterside_srinked.csv")
