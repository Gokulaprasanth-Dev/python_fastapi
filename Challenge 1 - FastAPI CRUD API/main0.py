from fastapi import FastAPI

app = FastAPI()

product = [
    {"id":1, "product":"p1"},
    {"id":2, "product":"p2"},
    {"id":3, "product":"p3"},
    {"id":4, "product":"p4"}
]

@app.get("/product")

def get_product():
    return product
