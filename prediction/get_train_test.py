import pandas as pd




df = pd.read_csv(SELECTED_TWITTER_IDS_PATH, header=0)
test = df.sample(frac=0.20, random_state=16)
train = df.drop(test.index)

print(len(train))
print(len(test))