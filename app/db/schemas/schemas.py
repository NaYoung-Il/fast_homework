from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.db.models.models import UserRole

# 1. User 스키마: 사용자 정보

# User의 기본 필드 정의
class UserBase(BaseModel):
    email: str
    username: str

# 회원가입 시 받을 데이터
class UserCreate(UserBase):
    password: str

# 로그인 시 받을 데이터
class UserLogin(BaseModel):
    email: str
    password: str

# 사용자 정보 수정 시 받을 데이터 (선택적 필드)
class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

# 데이터베이스에 저장된 형태 (해시된 비밀번호 포함)
class UserInDB(UserBase):
    id: int
    password: str
    role: UserRole

    # SQLAlchemy 모델 객체를 Pydantic 모델로 변환
    model_config = ConfigDict(from_attributes=True)

# 클라이언트에게 반환할 사용자 정보 (비밀번호 제외)
class UserRead(UserBase):
    id: int
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


# 2. Song 스키마: 노래 정보

# Song의 기본 필드 정의
class SongBase(BaseModel):
    title: str
    artist: str
    duration: int   # duration in seconds

# 노래를 생성할 때 받을 데이터 = SongBase와 동일
class SongCreate(SongBase):
    pass

# 노래 정보 수정 시 받을 데이터 (선택적 필드)
class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    duration: Optional[int] = None 

# 데이터베이스에 저장된 형태 = SongRead와 동일
class SongInDB(SongBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# 클라이언트에게 반환할 노래 정보
class SongRead(SongInDB):
    pass


# 3. Playlist 스키마: 플레이리스트 정보

# Playlist의 기본 필드 정의
class PlaylistBase(BaseModel):
    name: str
    desc: Optional[str] = None

# 플레이리스트를 생성할 때 받을 데이터
class PlaylistCreate(PlaylistBase):
    pass

# 플레이리스트 정보 수정 시 받을 데이터 (선택적 필드)
class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    desc: Optional[str] = None

# 데이터베이스에 저장된 형태
class PlaylistInDB(PlaylistBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

# 클라이언트에게 반환할 플레이리스트 정보
# 플레이리스트를 조회할 때, 소유자 정보와 노래 목록도 포함됨.
class PlaylistRead(PlaylistBase):
    id: int
    user: UserRead              # 소유자 정보 (중첩 모델)
    songs: List[SongRead] = []  # 노래 목록 (중첩 모델 리스트)

    model_config = ConfigDict(from_attributes=True)