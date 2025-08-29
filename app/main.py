from fastapi import FastAPI, Depends

from typing import Union, List

from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .schema import ItemCreated, ItemResponse
from .models import Item


Base.metadata.create_all(bind=engine) #Create Database, it cannot update schema
        
app = FastAPI()

@app.get("/items", response_model=List[ItemResponse])
def read_item(db: Session = Depends(get_db)):
    item = db.query(Item).all()
    return item
        

@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    return item


@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreated, db: Session = Depends(get_db)):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreated, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        return {"error": "Item not found"}
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        return {"error": "Item not found"}
    db.delete(db_item)
    db.commit()
    return {"message": f"Item with id {item_id} has been deleted"}