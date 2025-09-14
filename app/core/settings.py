from pydantic_settings import BaseSettings
from pydantic import Field
from datetime import timedelta

# settings.py : 설정 관리 모듈 
# .env 파일에서 환경 변수를 읽어와 애플리케이션 전체에서 사용 가능한 객체를 생성

class Settings(BaseSettings):
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: str = Field("3306", alias="DB_PORT")
    db_name: str = Field(..., alias="DB_NAME")

    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_algo: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire: int = Field(6000, alias="ACCESS_TOKEN_EXPIRE")
    refresh_token_expire: int = Field(604800, alias="REFRESH_TOKEN_EXPIRE")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"
        populate_by_name = True
    
    @property
    def tmp_db(self) -> str :   # "root:12345@localhost:3306/board"
        return f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def db_url(self) -> str :   # 비동기 DB URL
        return f"mysql+asyncmy://{self.tmp_db}"
    
    @property
    def sync_db_url(self) -> str :  # 동기 DB URL
        return f"mysql+pymysql://{self.tmp_db}"
    
    @property
    def access_token(self) :
        return timedelta(seconds=self.access_token_expire)
    
    @property
    def refresh_token(self) :
        return timedelta(seconds=self.refresh_token_expire)
    
settings = Settings() # settings 객체 생성, 애플리케이션 전역에서 사용 가능