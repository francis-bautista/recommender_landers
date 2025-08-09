from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from mlxtend.preprocessing import TransactionEncoder
import pickle
import pandas as pd

with open('unique_transactions_list.pkl','rb') as f:
    loaded_list = pickle.load(f)

te = TransactionEncoder()
te_ary = te.fit(loaded_list).transform(loaded_list, sparse=True)
df = pd.DataFrame.sparse.from_spmatrix(te_ary,columns=te.columns_)
df.columns = [str(i) for i in df.columns]
# print(df)

frequent_itemsets = apriori(df,min_support=0.0009,use_colnames=True,verbose=1)
rules = association_rules(frequent_itemsets,metric='confidence', min_threshold=0.001)
confidence_sort = rules.sort_values('confidence',ascending=False)
with open('rules.pkl','wb') as file:
    pickle.dump(confidence_sort,file)


print(confidence_sort.head(100))
