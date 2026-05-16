from datetime import datetime,timedelta,timezone

from jose import jwt,JWTError

from app.core.config import settings

def create_access_token(data: dict, expire_delta: timedelta | None) :
    
    to_encode = data.copy()
    
    if expire_delta :
        expire = datetime.now(timezone.utc) +expire_delta
    else :
        expire =datetime.now(timezone.utc) + timedelta(
            minutes = settings.access_token_expire_minutes
        )
    
    to_encode.update({
        "exp" : expire
    })
    
    encoded_jwt= jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        settings.jwt_algorithm
    )
    
    return  encoded_jwt

def verify_access_token(token: str):
    try:
        payload= jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None