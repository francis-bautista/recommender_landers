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
    """Get recommendations for a specific customer, excluding items already in cart."""
    cart = get_cart(customer_id)
    cart_items = [item['item_id'] for item in cart] if cart else []  # Extract item IDs from cart
    
    recommendations = get_recommendations(cart, rules)
    
    # Filter out items already in cart
    if not recommendations.empty:
        recommendations = recommendations[~recommendations['item'].isin(cart_items)]
    
    # Prepare response
    if recommendations.empty or len(recommendations) < 5:
        # Get popular items excluding cart items
        popular_filtered = popular_items[~popular_items['item'].isin(cart_items)]
        response = {
            "message": "No rule-based recommendations found (or not enough after cart exclusion), showing popular items",
            "recommendations": popular_filtered.head(5).to_dict(orient='records')
        }
    else:
        confident_recommendations = recommendations[recommendations['confidence'] > 0.2]
        
        if len(confident_recommendations) >= 5:
            final_recs = confident_recommendations.head(5)
            message = "Showing 5 confident recommendations above 20% confidence"
        else:
            padding_num = 5 - len(confident_recommendations)
            # Get popular items excluding cart items
            popular_filtered = popular_items[~popular_items['item'].isin(cart_items)]
            supplemental = popular_filtered.head(padding_num)
            final_recs = pd.concat([
                confident_recommendations,
                supplemental
            ], ignore_index=True)
            message = "Recommendations supplemented with popular items (excluding cart items)"
        
        response = {
            "message": message,
            "recommendations": final_recs.to_dict(orient='records')
        }
    
    return response
