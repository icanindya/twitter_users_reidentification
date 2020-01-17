import pandas as pd
data = [{'a': 1, 'b': 2, 'c': 6, 'd': 4},
        {'a': 5, 'b': 0, 'c': 9, 'd': 3},
        {'a': 4, 'b': 6, 'c': 2, 'd': 3},
        {'a': 5, 'b': 5, 'c': 1, 'd': 8},
        {'a': 1, 'b': 5, 'c': 3, 'd': 8}]

# With two column indices, values same
# as dictionary keys
df1 = pd.DataFrame(data, columns=['a', 'b', 'c', 'd'])

df1.set_index(['a', 'b'], inplace=True)

print(df1)

df1 = df1.groupby(level='a', axis=0).head(1)
print(df1)

print(' '.join('         '.split()) == '')