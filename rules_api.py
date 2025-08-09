from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
import json
import pickle
from collections import defaultdict
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load data at startup
with open('customer_entries.json', 'r') as file:
    custom_entries = json.load(file)

rules = pd.read_pickle('rules.pkl')
popular_items = pd.read_csv('popular.csv').drop('count', axis=1)

def get_cart(customer_id: int) -> List[str]:
    """Get cart items for a customer ID."""
    for item in custom_entries:
        if item['id'] == customer_id:
            return item['items']
    return []  # Return empty list if customer not found

def get_recommendations(cart: List[str], rules: pd.DataFrame) -> pd.DataFrame:
    """Generate recommendations based on association rules."""
    # Normalize column names for case insensitivity
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

    # Prepare data for DataFrame
    data = []
    for item, metrics in recommendations.items():
        data.append({
            'item': item,
            'confidence': max(metrics['confidence']) if metrics['confidence'] else 0,
            'lift': max(metrics['lift']) if metrics['lift'] else 0,
            'support': max(metrics['support']) if metrics['support'] else 0,
        })

    # Create and sort DataFrame
    df = pd.DataFrame(data)
    if not df.empty:
        df.sort_values(by=['confidence', 'lift', 'support'],
                      ascending=False, inplace=True)

    return df

@app.put("/input_customer_id/{customer_id}")
async def set_customer_id(customer_id: int) -> Dict[str, int]:
    """Set the customer ID for subsequent recommendations."""
    return {"customer_id": customer_id}

@app.get("/get_cart/{customer_id}")
async def cart(customer_id: int) -> Dict[str, List[str]]:
    """Get cart items for a specific customer."""
    cart_items = get_cart(customer_id)
    return {"items": cart_items}

@app.get("/get_recommendations/{customer_id}")
async def recommendations(customer_id: int) -> Dict[str, Any]:
    """Get recommendations for a specific customer."""
    cart = get_cart(customer_id)
#    if not cart:
#        return {"message": "Customer not found or cart is empty", "recommendations": []}
    
    recommendations = get_recommendations(cart, rules)
    
    # Prepare response
    if recommendations.empty:
        response = {
            "message": "No rule-based recommendations found, showing popular items",
            "recommendations": popular_items.head(5).to_dict(orient='records')
        }
    else:
        confident_recommendations = recommendations[recommendations['confidence'] > 0.2]
        
        if len(confident_recommendations) >= 5:
            final_recs = confident_recommendations.head(5)
            message = "Showing 5 confident recommendations above 20% confidence"
        else:
            padding_num = 5 - len(confident_recommendations)
            supplemental = popular_items.head(padding_num)
            final_recs = pd.concat([
                confident_recommendations,
                supplemental
            ], ignore_index=True)
            message = "Recommendations supplemented with popular items"
        
        response = {
            "message": message,
            "recommendations": final_recs.to_dict(orient='records')
        }
    
    # output_file = f'recommendations_{customer_id}.csv'
    # pd.DataFrame(response['recommendations']).to_csv(output_file, index=False)
    
    return response
