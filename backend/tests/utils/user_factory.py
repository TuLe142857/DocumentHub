from app.models import User, UserProfile, Role
from sqlalchemy.orm import Session


class UserFactory:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(
        self,
        username: str,
        email: str,
        password: str,
        role: Role | None = None,
        is_active: bool = True,
    ) -> User:
        """

        Args:
            username:
            email:
            password:
            role: role. Default None will use role "USER"

        Returns:
        """
        user = User(
            email=email,
            username=username,
            role=role or Role.get_or_create("USER", self.db_session),
            profile=UserProfile(),
            is_active=is_active,
        )
        user.set_password(password)
        self.db_session.add(user)
        self.db_session.commit()
        return user

    def create_many(
        self,
        n: int,
        username_prefix: str = "user_",
        email_prefix: str = "email_",
        password: str = "password123",
        role: Role | None = None,
    ) -> list[User]:
        role: Role = role or Role.get_or_create("USER", self.db_session)
        users = [
            User(
                username=f"{username_prefix}_{_}",
                email=f"{email_prefix}_{_}",
                role=role,
                profile=UserProfile(),
                password_hash=password,
            )
            for _ in range(n)
        ]
        for user in users:
            # user.set_password(password)
            self.db_session.add(user)
        self.db_session.commit()
        return users
