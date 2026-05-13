# Production Grade FastAPI Project

## Features Included

- Challenge 1 — CRUD APIs
- Challenge 2 — PostgreSQL + SQLAlchemy ORM
- Challenge 3 — Async programming
- Challenge 4 — JWT Authentication + Role based access
- Clean folder structure
- Production-ready architecture

---

# 1. Install Packages

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart
```

---

# 2. Folder Structure

```text
project/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── dependencies.py
│   ├── config.py
│   │
│   ├── routers/
│   │   ├── auth_router.py
│   │   ├── product_router.py
│   │   └── profile_router.py
│   │
│   └── services/
│       └── dashboard_service.py
│
└── requirements.txt
```

---

# 3. config.py

```python
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

---

# 4. database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/fastapi_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
```

---

# 5. models.py

```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database import Base


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    price = Column(Float, nullable=False)

    category = Column(String, nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)

    password = Column(String, nullable=False)

    role = Column(String, default="user")
```

---

# 6. schemas.py

```python
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):

    name: str = Field(..., min_length=1)

    price: float = Field(..., gt=0)

    category: str


class LoginRequest(BaseModel):

    username: str

    password: str
```

---

# 7. auth.py

```python
from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException

from app.config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(hours=1)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



def verify_token(token: str):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
```

---

# 8. dependencies.py

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth import verify_token

security = HTTPBearer()



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    payload = verify_token(token)

    return payload



def admin_only(user=Depends(get_current_user)):

    if user.get("role") != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user
```

---

# 9. routers/auth_router.py

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import LoginRequest
from app.auth import verify_password, create_access_token

router = APIRouter()


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.username == data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token({
        "sub": user.username,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
```

---

# 10. routers/product_router.py

```python
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

    return result


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
```

---

# 11. routers/profile_router.py

```python
from fastapi import APIRouter, Depends

from app.dependencies import get_current_user

router = APIRouter()


@router.get("/profile")
def get_profile(user=Depends(get_current_user)):

    return {
        "username": user.get("sub"),
        "role": user.get("role")
    }
```

---

# 12. services/dashboard_service.py

```python
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
```

---

# 13. main.py

```python
from fastapi import FastAPI

from app.database import engine
from app.models import Base

from app.routers.auth_router import router as auth_router
from app.routers.product_router import router as product_router
from app.routers.profile_router import router as profile_router

app = FastAPI(
    title="Production FastAPI App"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(profile_router)
```

---

# 14. Create First Admin User

Create temporary file:

```python
from app.database import SessionLocal
from app.models import User
from app.auth import hash_password


db = SessionLocal()

admin = User(
    username="admin",
    password=hash_password("admin123"),
    role="admin"
)


db.add(admin)

db.commit()

print("Admin created")
```

Run:

```bash
python create_admin.py
```

---

# 15. Run Server

```bash
uvicorn app.main:app --reload
```

---

# 16. Swagger Docs

```text
http://127.0.0.1:8000/docs
```

---

# Authentication Flow

1. POST `/login`
2. Copy JWT token
3. Click Authorize in Swagger
4. Enter:

```text
Bearer YOUR_TOKEN
```

5. Access protected routes

---

# Production Concepts Used

- JWT Authentication
- Password hashing
- Role based access control
- SQLAlchemy ORM
- PostgreSQL
- Async programming
- Dependency injection
- Modular architecture
- Error handling
- Validation
- Indexed queries

