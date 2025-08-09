import pandas as pd
import pickle as pk
import sys

file = sys.argv[1]

df = pd.read_csv(file)

# #df['article'].apply(lambda x : print(x))
# reciets = df.groupby('transact').agg({
#     'customer_id' : 'first',
#     'article' : list,
#     'date_col' : 'first'
#     })

df = df.rename(columns={'article':'item'})
popular = df['item'].value_counts()
print(popular.head())
popular.to_csv('popular.csv',index=True)
# reciets.to_csv('receits.csv',index=False)
