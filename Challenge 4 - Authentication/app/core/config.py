from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    app_name : str 
    app_version : str

    mongodb_url : str 
    database_name : str
    
    jwt_secret_key : str 
    jwt_algorithm : str 
    access_token_expire_minutes : int 

    aws_access_key_id : str
    aws_secret_access_key : str
    aws_region : str
    aws_s3_bucket_name : str
    
    model_config =ConfigDict(
        env_file = ".env",
        extra = "ignore",
        frozen = True
    )

settings = Settings()