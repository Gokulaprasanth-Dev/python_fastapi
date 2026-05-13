import asyncio


async def fetch_product_data():

    await asyncio.sleep(1)

    return {
        "total_products": 100
    }


async def fetch_user_data():

    await asyncio.sleep(1)

    return {
        "total_users": 50
    }


async def dashboard_summary():

    results = await asyncio.gather(
        fetch_product_data(),
        fetch_user_data(),
        return_exceptions=True
    )

    return {
        "products": results[0],
        "users": results[1]
    }
