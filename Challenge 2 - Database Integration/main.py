# from fastapi import FastAPI

# from database import engine
# from models import Product

# app = FastAPI()

# Product.metadata.create_all(bind=engine)

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, get_db
from models import Product

from sqlalchemy import func

app = FastAPI()

Product.metadata.create_all(bind=engine)


class ProductCreate(BaseModel):

    name: str
    price: float
    category: str


@app.post("/products")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):

    new_product = Product(
        name=product.name,
        price=product.price,
        category=product.category
    )

    db.add(new_product)

    db.commit()

    db.refresh(new_product)

    return new_product


@app.get("/products")
def get_products(db: Session = Depends(get_db)):

    products = db.query(Product).all()

    return products


@app.get("/products/{id}")
def get_product(id: int, db: Session = Depends(get_db)):

    product = db.query(Product).filter(Product.id == id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product

@app.get("/products/stats/average-price")
def average_price_by_category(db: Session = Depends(get_db)):

    result = (
        db.query(
            Product.category,
            func.avg(Product.price).label("average_price")
        )
        .group_by(Product.category)
        .order_by(func.avg(Product.price).desc())
        .all()
    )

    return result