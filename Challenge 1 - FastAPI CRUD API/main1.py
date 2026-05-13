from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

products = [
    {"id":1, "name":"p1", "price":5000, "category":"Electronics"},
    {"id":2, "name":"p2", "price":5000, "category":"Electronics"},
    {"id":3, "name":"p3", "price":5000, "category":"Electronics"},
    {"id":4, "name":"p4", "price":5000, "category":"Electronics"}
]
class Product(BaseModel):
    name: str = Field(...,min_length=1)
    price: float = Field(...,gt=0)
    category:str
    
@app.get("/products")
def get_products():
    return products
@app.post("/products")
def create_product(product: Product):
    new_product ={"id":len(products)+1, "name":product.name, "price":product.price, "category":product.category}
    products.append(new_product)
    return {
        "message": "Product created",
        "product": new_product
    }