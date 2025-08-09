import json
import pickle
from collections import defaultdict
import pandas as pd

rules = pd.read_pickle('rules.pkl')  

with open('customer_entries.json', 'r') as file:
    custom_entries = json.load(file)
    
def get_cart(custom_entries,cust_id):    
    for item in custom_entries:
        # print(item)
        if item['id'] == cust_id:
            # print("match")
            return item['items']
            break

cust_id = int(input("Input Customer ID: "))
cart = get_cart(custom_entries,cust_id)

def get_recommendations(cart, rules):
    # norm  column names for case insensitivity
    cols = {col.lower(): col for col in rules.columns}
    
    recommendations = defaultdict(lambda: {
        'confidence': [],
        'lift': [],
        'support': []
    })
    cart_set = set(cart)

    for _, rule in rules.iterrows():
        antecedent = set(rule[cols['antecedents']])
        consequent = set(rule[cols['consequents']])

        if antecedent.issubset(cart_set):
            for item in consequent - cart_set:
                recommendations[item]['confidence'].append(rule[cols['confidence']])
                recommendations[item]['lift'].append(rule[cols['lift']])
                recommendations[item]['support'].append(rule[cols['support']])

    # prep data for df
    data = []
    for item, metrics in recommendations.items():
        data.append({
            'Item': item,
            'Confidence': max(metrics['confidence']) if metrics['confidence'] else 0,
            'Lift': max(metrics['lift']) if metrics['lift'] else 0,
            'Support': max(metrics['support']) if metrics['support'] else 0,
        })

    # creating and sorting df
    df = pd.DataFrame(data)
    if not df.empty:
        # df.sort_values(by=['Confidence', 'Lift', 'Support'],
        df.sort_values(by=['Lift', 'Confidence', 'Support'],
        # df.sort_values(by=['Support', 'Lift', 'Support'],
                     ascending=False, inplace=True)

    return df

recommendations = get_recommendations(cart, rules)
popular_count = pd.read_csv('popular.csv')
popular = popular_count.drop('count',axis=1)
# print(recommendations)
if recommendations.empty: 
    print("recommended items based on popularity")
    print(popular.head(3))
    recommendations = popular.head(3)
else:
    confident_recommendations = recommendations[recommendations['Confidence']> 0.2]
    print(confident_recommendations)
    if len(confident_recommendations) >= 5:
        print("showing 5 confident recommendations above 20%:")
        recommendations = confident_recommendations.head(5)

    if len(confident_recommendations) <= 4:
        print("recommendations supplemented with popular items:")
        # if less than 3 pad with popular items to make it 3
        if len(confident_recommendations) <= 2:
            padding_num = 5 - len(confident_recommendations)
            print(type(padding_num), padding_num)
            supplemental = popular.head(padding_num)
            common_columns = list(set(confident_recommendations.columns) & set(popular.columns))
            #combine the confident recommendations with the popular ones
            recommendations = pd.concat([
                # recommendation[common_columns].head(3),
                confident_recommendations.head(3),
                supplemental[common_columns].head(padding_num)
            ], ignore_index=True)

output_file = 'product_recommendations.csv'
recommendations.to_csv(output_file, index=False, float_format='%.4f')
print(f"Recommendations saved to {output_file}")


# if len(recommendations) <= 5:
#     print("less than 5")
# if len(recommendations) >= 5:
#     print("more than 5")
# if recommendations.empty:
#     print("No recommendations found for this cart.")
#     print("here are the most popular items:\n")
#     print(popular.head(5))
# else:
#     # Save to CSV
#     output_file = 'product_recommendations.csv'
#     recommendations.to_csv(output_file, index=False, float_format='%.4f')
#     print(f"Recommendations saved to {output_file}")
#     print("\nTop Recommendations:")
#     print(recommendations.head(3).to_string(index=False))
