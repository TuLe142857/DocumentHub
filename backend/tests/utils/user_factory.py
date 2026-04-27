from app.models import User, UserProfile, Role
from sqlalchemy.orm import Session


class UserFactory:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(
        self, username: str, email: str, password: str, role: Role | None = None
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
        )
        user.set_password(password)
        self.db_session.add(user)
        self.db_session.commit()
        return user

    def create_many(self):
        pass
