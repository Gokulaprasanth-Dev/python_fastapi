from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Product
from app.schemas import ProductCreate
from app.dependencies import get_current_user, admin_only

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("")
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    new_product = Product(
        name=product.name,
        price=product.price,
        category=product.category
    )

    db.add(new_product)

    db.commit()

    db.refresh(new_product)

    return new_product


@router.get("")
async def get_products(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    return db.query(Product).all()


@router.get("/stats/average-price")
async def average_price(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    result = (
        db.query(
            Product.category,
            func.avg(Product.price).label("average_price")
        )
        .group_by(Product.category)
        .order_by(func.avg(Product.price).desc())
        .all()
    )

    return [
    {
        "category": item.category,
        "average_price": float(item.average_price)
    }
    for item in result
]


@router.get("/{id}")
async def get_product(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    product = db.query(Product).filter(
        Product.id == id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.delete("/{id}")
async def delete_product(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(admin_only)
):

    product = db.query(Product).filter(
        Product.id == id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)

    db.commit()

    return {
        "message": "Product deleted"
    }
