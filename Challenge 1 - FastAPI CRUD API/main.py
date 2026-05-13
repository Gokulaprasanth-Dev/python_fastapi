from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from jose import jwt, JWTError

app = FastAPI()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

security =HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
        
        
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
def get_products(user=Depends(verify_token)):
    return products
@app.post("/products")
def create_product(product: Product, user=Depends(verify_token)):
    new_product ={"id":len(products)+1, "name":product.name, "price":product.price, "category":product.category}
    products.append(new_product)
    return {
        "message": "Product created",
        "product": new_product
    }
    
@app.get("/products/{id}")
def get_produuct(id: int, user=Depends(verify_token)):
    
    for product in products:
        if product["id"] == id:
            return product
        
    raise HTTPException(
        status_code=404,
        detail="Product Not Found"
    )
