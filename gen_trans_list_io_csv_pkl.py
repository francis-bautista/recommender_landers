import pandas as pd
import pickle
import sys

file = sys.argv[1]

# Load the CSV file into a DataFrame
df = pd.read_csv(file)  # Replace 'your_file.csv' with your actual file path

# Group by transaction_id and aggregate products into a list
result = df.groupby('transact').agg({
    'customer_id': 'first',  # Keep the customer ID (assuming it's the same for all rows of same transaction)
    'article': list,      # Collect all product_ids into a list
    'date_col': 'first'          # Keep the transaction date
}).reset_index()

# If you only want transaction_id and product list:
simple_result = df.groupby('transact')['article'].apply(list).reset_index()# Get unique customer_id and transact_id pairs
list_on = df.groupby('transact')['article'].apply(list)

lists_only = df.groupby('transact')['article'].apply(list).tolist()

with open('unique_transactions_list.pkl', 'wb') as f:
    pickle.dump(lists_only, f)

#print(lists_only)
#list_on.to_json('out.json', indent=4) 
#result.to_csv('result.csv',index=False)
#simple_result.to_csv('out.csv', index=False)
#lists_only.to_csv('lists.csv', index=False)

