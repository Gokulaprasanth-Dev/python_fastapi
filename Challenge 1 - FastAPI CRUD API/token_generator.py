from jose import jwt

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

data = {
    "username": "admin"
}

token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

print(token)