from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: str
    price: float
    
class ItemCreated(ItemBase):
    #logic
    pass

class ItemResponse(ItemBase):
    id: int
    class Config:
        from_attributes = True