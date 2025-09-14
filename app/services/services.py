from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.schemas import UserCreate, UserLogin, SongCreate, SongUpdate, PlaylistCreate, PlaylistUpdate
from app.db.cruds.cruds import UserCrud, SongCrud, PlaylistCrud, PlaylistSongCrud
from fastapi import HTTPException
from app.core.jwt_context import get_pwd_hash, verify_pwd, create_access_token, create_refresh_token

# 1. User(사용자)와 관련된 서비스 클래스
class UserService:

    # DB에서 해당 id의 사용자 조회
    @staticmethod
    async def get_user(db: AsyncSession, id: int):
        db_user = await UserCrud.get_id(db, id)
        if not db_user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        return db_user
    
    # 회원가입 서비스
    @staticmethod
    async def signup(db: AsyncSession, user:UserCreate):

        # 중복된 username 또는 email이 있는지 확인
        if await UserCrud.get_username(db, user.username):
            raise HTTPException(status_code=400, detail="이미 사용 중인 username입니다.")
        if await UserCrud.get_email(db, user.email):
            raise HTTPException(status_code=400, detail="이미 사용 중인 email입니다.")
        
        # 중복 없으면 username, email, password를 DB에 저장 (비밀번호는 해시값으로 저장)
        user.password = await get_pwd_hash(user.password)

        try:
            db_user = await UserCrud.create(db, user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except Exception:
            raise HTTPException(status_code=401, detail="잘못된 이메일 또는 비밀번호입니다.")
    
    # 로그인 서비스
    @staticmethod
    async def login(db: AsyncSession, user: UserLogin) -> tuple:
        
        db_user = await UserCrud.get_email(db, user.email)
        if not db_user or not await verify_pwd(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="잘못된 이메일 또는 비밀번호입니다.")
        
        access_token = create_access_token(db_user.id)
        refresh_token = create_refresh_token(db_user.id)

        updated_user = await UserCrud.update_refresh_token_id(db, db_user.id, refresh_token)
        await db.commit()
        await db.refresh(updated_user)

        return updated_user, access_token, refresh_token


# 2. Song(노래)과 관련된 서비스 클래스
class SongService:
    
    # DB에서 해당 id의 노래 조회
    @staticmethod
    async def get_song(db: AsyncSession, id: int):
        db_song = await SongCrud.get_id(db, id)
        if not db_song:
            raise HTTPException(status_code=404, detail="노래를 찾을 수 없습니다.")
        return db_song
    
    # 전체 노래 조회
    @staticmethod
    async def get_all_songs(db: AsyncSession):
        return await SongCrud.get_all(db)
    
    # 노래 생성 서비스
    @staticmethod
    async def create_song(db: AsyncSession, song: SongCreate):
        db_song = await SongCrud.create(db, song)
        await db.commit()
        await db.refresh(db_song)
        return db_song
    
    # 노래 수정 서비스
    @staticmethod
    async def update_song(db: AsyncSession, id: int, song_update: SongUpdate):
        db_song = await SongService.get_song(db, id) # get_song으로 노래 존재 여부 확인
        updated_song = await SongCrud.update_by_id(db, id, song_update)
        await db.commit()
        await db.refresh(updated_song)
        return updated_song
    
    # 노래 삭제 서비스
    @staticmethod
    async def delete_song(db: AsyncSession, id: int):
        db_song = await SongService.get_song(db, id) # get_song으로 노래 존재 여부 확인
        deleted_song = await SongCrud.delete_by_id(db, id)
        await db.commit()
        return deleted_song


# 3. Playlist(플레이리스트)와 관련된 서비스 클래스
class PlaylistService:
    
    # DB에서 해당 id의 플레이리스트 조회
    @staticmethod
    async def get_playlist(db: AsyncSession, id: int):
        db_playlist = await PlaylistCrud.get_id(db, id)
        if not db_playlist:
            raise HTTPException(status_code=404, detail="플레이리스트를 찾을 수 없습니다.")
        return db_playlist
    
    # 해당 사용자의 모든 플레이리스트 조회
    @staticmethod
    async def get_user_playlists(db: AsyncSession, user_id: int):
        return await PlaylistCrud.get_all_by_user_id(db, user_id)
    
    # 플레이리스트 생성 서비스
    @staticmethod
    async def create_playlist(db: AsyncSession, playlist: PlaylistCreate, user_id: int):
        
        # 객체를 생성하고 세션에 추가
        db_playlist = await PlaylistCrud.create(db, playlist, user_id)
        # commit 하기 전에 id를 변수에 저장
        playlist_id = db_playlist.id
        # 데이터베이스에 변경사항을 커밋
        await db.commit()
        # 미리 저장해 둔 id를 사용하여 관계가 로드된 완전한 객체를 조회하여 반환
        return await PlaylistCrud.get_id(db, playlist_id)
    
    # 플레이리스트 수정 서비스
    @staticmethod
    async def update_playlist(db: AsyncSession, id: int, playlist_update: PlaylistUpdate):
        db_playlist = await PlaylistService.get_playlist(db, id) # get_playlist으로 플레이리스트 존재 여부 확인
        updated_playlist = await PlaylistCrud.update_by_id(db, id, playlist_update)
        await db.commit()
        await db.refresh(updated_playlist)
        return updated_playlist
    
    # 플레이리스트 삭제 서비스
    @staticmethod
    async def delete_playlist(db: AsyncSession, id: int):
        db_playlist = await PlaylistService.get_playlist(db, id) # get_playlist으로 플레이리스트 존재 여부 확인
        deleted_playlist = await PlaylistCrud.delete_by_id(db, id)
        await db.commit()
        return deleted_playlist
    

# 4. PlaylistSong(플레이리스트-노래 관계)와 관련된 서비스 클래스
class PlaylistSongService:
    
    # 플레이리스트에 노래 추가 서비스
    @staticmethod
    async def add_song_to_playlist(db: AsyncSession, playlist_id: int, song_id: int):

        # 플레이리스트와 노래가 DB에 존재하는지 확인
        db_playlist = await PlaylistService.get_playlist(db, playlist_id)
        db_song = await SongService.get_song(db, song_id)

        # CRUD 호출하여 노래 추가
        updated_playlist = await PlaylistSongCrud.add_song_to_playlist(db, db_playlist, db_song)
        await db.commit()
        await db.refresh(updated_playlist)
        return updated_playlist
    
    # 플레이리스트에서 노래 제거 서비스
    @staticmethod
    async def remove_song_from_playlist(db: AsyncSession, playlist_id: int, song_id: int):

        # 플레이리스트와 노래가 DB에 존재하는지 확인
        db_playlist = await PlaylistService.get_playlist(db, playlist_id)
        db_song = await SongService.get_song(db, song_id)

        # CRUD 호출하여 노래 제거
        updated_playlist = await PlaylistSongCrud.remove_song_from_playlist(db, db_playlist, db_song)
        await db.commit()
        await db.refresh(updated_playlist)
        return updated_playlist