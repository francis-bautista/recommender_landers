import json
import random
import pandas as pd
import pickle
import sys

file = sys.argv[1]

data = pd.read_csv(file)
# data = data.drop('customer',axis=1)
# print(data.head())
# print(data['article'].drop_duplicates().to_list())
# print(data['customer_id'].drop_duplicates().to_list())

items = data['article'].drop_duplicates().to_list()
customers = data['customer_id'].drop_duplicates().to_list()

# print(len(data['customer_id'].to_list()))
# print(len(customers))
# print(random.choice(customers))
# print(random.choice(items))
# print(random.randrange(1,4))

data = []
for x in range(100):
    cust_id = random.choice(customers)
    item_num = random.randrange(1,4)
    item_list = []
    for x in range(item_num):
        # item_list.append(str(random.choice(items)))
        item_list.append(str(random.choice(items)))
    entry = dict(id = cust_id,items = item_list)
    data.append(entry)

# for x in data:
#     print(x)
#     print("\n")

with open("customer_entries.json", "w") as final:
	json.dump(data, final, indent=4, sort_keys=True)

#files.download('customer_entries.json')



