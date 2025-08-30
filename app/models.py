from sqlmodel import Field, SQLModel
from typing import Optional
# ORM Class
class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    price: float = Field(default=0.0)
    