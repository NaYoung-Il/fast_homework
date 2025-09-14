- 주제 : 음원 스트리밍 사이트
- 핵심 기능
    - 사용자 가입 및 로그인
    - 노래 CRUD
      → 조회는 모든 사용자 가능 / 나머지 기능은 관리자만 가능 (role : USER/ADMIN)
    - 플레이리스트 CRUD
      → 사용자 본인만 가능
    - 플레이리스트에 노래 추가/제거
      → 사용자 본인만 가능
- 테이블 목록
    - users : 사용자 (id, username, email, password, role)
    - songs : 노래 정보 (id, title, artist, duration)
    - playlists : 플레이리스트 (id, name, desc, user_id(FK))
    - playlist_songs : 플레이리스트, 노래 N:M 연결 테이블 (playlist_id, song_id)
