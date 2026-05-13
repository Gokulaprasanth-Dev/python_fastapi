import asyncio

from fastapi import FastAPI, HTTPException

app = FastAPI()


# -----------------------------------
# Async services
# -----------------------------------

async def fetch_product(product_id: int):

    await asyncio.sleep(1)

    products = {
        1: {"id": 1, "name": "Laptop", "price": 55000},
        2: {"id": 2, "name": "Phone", "price": 30000}
    }

    product = products.get(product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


async def fetch_user(user_id: int):

    await asyncio.sleep(1)

    users = {
        101: {"id": 101, "username": "admin"},
        102: {"id": 102, "username": "gokul"}
    }

    user = users.get(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# -----------------------------------
# Combined async endpoint
# -----------------------------------

@app.get("/dashboard")
async def get_dashboard(product_id: int, user_id: int):

    tasks = [
        fetch_product(product_id),
        fetch_user(user_id)
    ]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    product_result = results[0]
    user_result = results[1]

    response = {
        "success": True,
        "data": {},
        "errors": []
    }

    # Product result handling
    if isinstance(product_result, Exception):

        response["success"] = False

        response["errors"].append({
            "service": "product_service",
            "message": str(product_result)
        })

    else:
        response["data"]["product"] = product_result

    # User result handling
    if isinstance(user_result, Exception):

        response["success"] = False

        response["errors"].append({
            "service": "user_service",
            "message": str(user_result)
        })

    else:
        response["data"]["user"] = user_result

    return response