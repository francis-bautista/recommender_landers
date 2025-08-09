from fastapi import FastAPI
import use_rules

app = FastAPI()

@app.get("/get_message")
async def read_root():
    return {"Message":"My First API"}

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id" : item_id}

@app.get("/rules")
async def get_rec():
    get_recommendations()
    return None

