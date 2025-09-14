from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.models import User, Song, Playlist
from app.db.schemas.schemas import UserCreate, UserUpdate, SongCreate, SongUpdate, PlaylistCreate, PlaylistUpdate
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# 1. User와 관련된 CRUD 기능 클래스
class UserCrud:

    # id로 조회 : select * from users where id = :id
    # 결과가 1개면 객체 반환, 없으면 None 반환
    @staticmethod
    async def get_id(db:AsyncSession, id:int) -> User | None:
        result = await db.execute(select(User).filter(User.id == id))
        return result.scalar_one_or_none()
    
    # 생성
    @staticmethod
    async def create(db:AsyncSession, user:UserCreate) -> User :
        db_user = User(**user.model_dump())
        db.add(db_user)
        await db.flush()
        return db_user
    
    # 삭제
    @staticmethod
    async def delete_by_id(db:AsyncSession, id:int):
        db_user = await db.get(User, id)
        if db_user:
            await db.delete(db_user)
            await db.flush()
            return db_user
        return None
    
    # username 값 얻어오기
    @staticmethod
    async def get_username(db: AsyncSession, username: str):
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()
    
    # email 값 얻어오기
    @staticmethod
    async def get_email(db: AsyncSession, email: str):
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    # 수정
    @staticmethod
    async def update_by_id(db:AsyncSession, id:int, user:UserUpdate):
        db_user = await db.get(User, id)
        if db_user:
            # PATCH (요청에서 전달된 필드만 업데이트)
            update_user = user.model_dump(exclude_unset=True)   
            for i, j in update_user.items():
                setattr(db_user, i, j)
            await db.flush()
            return db_user
        return None
    
    # id로 사용자 조회해서 존재하면 refresh_token 업데이트
    @staticmethod
    async def update_refresh_token_id(db:AsyncSession, id:int, refresh_token:str):
        db_user = await db.get(User, id)
        if db_user:
            db_user.refresh_token = refresh_token
            await db.flush()
        return db_user
    

# 2. Song과 관련된 CRUD 기능 클래스
class SongCrud:

    # id로 조회 : select * from songs where id = :id
    @staticmethod
    async def get_id(db:AsyncSession, id:int) -> Song | None:
        result = await db.execute(select(Song).filter(Song.id == id))
        return result.scalar_one_or_none()
    
    # 생성
    @staticmethod
    async def create(db:AsyncSession, song:SongCreate) -> Song :
        db_song = Song(**song.model_dump())
        db.add(db_song)
        await db.flush()
        return db_song
    
    # 모든 노래 목록 조회
    @staticmethod
    async def get_all(db:AsyncSession) -> list[Song]:
        result = await db.execute(select(Song))
        return result.scalars().all()
    
    # 삭제
    @staticmethod
    async def delete_by_id(db:AsyncSession, id:int):
        db_song = await db.get(Song, id)
        if db_song:
            await db.delete(db_song)
            await db.flush()
            return db_song
        return None
    
    # 수정
    @staticmethod
    async def update_by_id(db:AsyncSession, id:int, song:SongUpdate):
        db_song = await db.get(Song, id)
        if db_song:
            # PATCH (요청에서 전달된 필드만 업데이트)
            update_song = song.model_dump(exclude_unset=True)   
            for i, j in update_song.items():
                setattr(db_song, i, j)
            await db.flush()
            return db_song
        return None


# 3. Playlist와 관련된 CRUD 기능 클래스
class PlaylistCrud:

    # id로 조회 : select * from playlists where id = :id
    @staticmethod
    async def get_id(db:AsyncSession, id:int) -> Playlist | None:
        # user, songs 관계를 즉시 로딩하도록 옵션 추가
        stmt = (
            select(Playlist)
            .options(
                selectinload(Playlist.user), 
                selectinload(Playlist.songs)
            )
            .filter(Playlist.id == id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    # 생성
    @staticmethod
    async def create(db:AsyncSession, playlist:PlaylistCreate, user_id:int) -> Playlist :
        db_playlist = Playlist(**playlist.model_dump(), user_id=user_id)
        db.add(db_playlist)
        await db.flush()
        return db_playlist
    
    # 특정 사용자의 모든 플레이리스트 조회
    @staticmethod
    async def get_all_by_user_id(db: AsyncSession, user_id: int) -> list[Playlist]:
        # user, songs 관계를 즉시 로딩하도록 옵션 추가
        stmt = (
            select(Playlist)
            .options(
                selectinload(Playlist.user), 
                selectinload(Playlist.songs)
            )
            .filter(Playlist.user_id == user_id)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    # 삭제
    @staticmethod
    async def delete_by_id(db:AsyncSession, id:int):
        db_playlist = await db.get(Playlist, id)
        if db_playlist:
            await db.delete(db_playlist)
            await db.flush()
            return db_playlist
        return None
    
    # 수정
    @staticmethod
    async def update_by_id(db:AsyncSession, id:int, playlist:PlaylistUpdate):
        db_playlist = await db.get(Playlist, id)
        if db_playlist:
            # PATCH (요청에서 전달된 필드만 업데이트)
            update_playlist = playlist.model_dump(exclude_unset=True)   
            for i, j in update_playlist.items():
                setattr(db_playlist, i, j)
            await db.flush()
            return db_playlist
        return None


# 4. 플레이리스트에서 노래 추가/제거하는 CRUD 기능 클래스
class PlaylistSongCrud:

    # 플레이리스트에 노래 추가
    @staticmethod
    async def add_song_to_playlist(db: AsyncSession, playlist: Playlist, song: Song) -> Playlist:
        if song not in playlist.songs:
            playlist.songs.append(song)
            await db.flush()
        return playlist

    # 플레이리스트에서 노래 제거
    @staticmethod
    async def remove_song_from_playlist(db: AsyncSession, playlist: Playlist, song: Song) -> Playlist:
        if song in playlist.songs:
            playlist.songs.remove(song)
            await db.flush()
        return playlist
