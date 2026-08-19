from sqlalchemy.orm import Session

from app.core.errors import ValidationError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories.users import UserRepository
from app.schemas import UserCreate
from app.services.email_service import EmailService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: UserCreate) -> User:
        if self.users.get_by_email(payload.email):
            raise ValidationError("Email already registered")
        user = User(
            email=payload.email.lower(),
            display_name=payload.display_name.strip(),
            password_hash=hash_password(payload.password),
        )
        self.users.add(user)
        self.db.commit()
        self.db.refresh(user)
        EmailService().send_welcome_email(user.email, user.display_name)
        return user

    def login(self, email: str, password: str) -> str:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise ValidationError("Invalid credentials")
        return create_access_token(user.id)
