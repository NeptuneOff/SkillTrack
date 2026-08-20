from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token
from app.models import User
from app.repositories import SqlAlchemySkillTrackRepository, get_repository

bearer = HTTPBearer()

def current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    repository: SqlAlchemySkillTrackRepository = Depends(get_repository),
) -> User:
    user_id = decode_access_token(creds.credentials)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = repository.user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
