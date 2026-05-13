# import asyncio


# async def fetch_product_data():

#     await asyncio.sleep(1)

#     return {
#         "total_products": 100
#     }


# async def fetch_user_data():

#     await asyncio.sleep(1)

#     return {
#         "total_users": 50
#     }


# async def dashboard_summary():

#     results = await asyncio.gather(
#         fetch_product_data(),
#         fetch_user_data(),
#         return_exceptions=True
#     )

#     return {
#         "products": results[0],
#         "users": results[1]
#     }

import asyncio

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Product, User


async def fetch_product_data(db: Session):

    await asyncio.sleep(0)

    total_products = db.query(Product).count()

    average_price = db.query(
        func.avg(Product.price)
    ).scalar()

    return {
        "total_products": total_products,
        "average_price": float(average_price or 0)
    }


async def fetch_user_data(db: Session):

    await asyncio.sleep(0)

    total_users = db.query(User).count()

    admin_users = db.query(User).filter(
        User.role == "admin"
    ).count()

    return {
        "total_users": total_users,
        "admin_users": admin_users
    }


async def dashboard_summary(db: Session):

    results = await asyncio.gather(
        fetch_product_data(db),
        fetch_user_data(db),
        return_exceptions=True
    )

    product_result = results[0]

    user_result = results[1]

    response = {
        "success": True,
        "data": {},
        "errors": []
    }

    # Product data
    if isinstance(product_result, Exception):

        response["success"] = False

        response["errors"].append({
            "service": "product_service",
            "message": str(product_result)
        })

    else:
        response["data"]["products"] = product_result

    # User data
    if isinstance(user_result, Exception):

        response["success"] = False

        response["errors"].append({
            "service": "user_service",
            "message": str(user_result)
        })

    else:
        response["data"]["users"] = user_result

    return response