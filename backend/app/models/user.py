from __future__ import annotations

import datetime
import enum
from typing import List

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlalchemy import (
    Boolean,
    DateTime,
    Engine,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    or_,
    select,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from .base_model import BaseModel

password_hash = PasswordHash((Argon2Hasher(),))


class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class Role(BaseModel):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    users: Mapped[List["User"]] = relationship(back_populates="role")

    @staticmethod
    def get_or_create(role_name: str, engine: Engine) -> "int":
        """

        Args:
            role_name:
            engine:

        Returns: role.id

        """
        with Session(engine) as session:
            role_in_db = session.execute(
                select(Role).where(Role.name == role_name)
            ).scalar_one_or_none()
            if role_in_db:
                return role_in_db.name

            # try to create new role
            new_role = Role(name=role_name)
            session.add(new_role)
            try:
                session.commit()
                return new_role.id
            except IntegrityError:
                # may be some thread has created this new role
                session.rollback()
                return session.execute(
                    select(Role.id).where(Role.name == role_name)
                ).scalar_one_or_none()


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="1")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), server_onupdate=func.now()
    )

    role: Mapped["Role"] = relationship("Role", back_populates="users")
    documents: Mapped[List["Document"]] = relationship(back_populates="owner")
    liked_documents: Mapped[List["DocumentLike"]] = relationship(back_populates="user")
    profile: Mapped["UserProfile"] = relationship(back_populates="user")
    collections: Mapped[List["Collection"]] = relationship(back_populates="owner")

    def set_password(self, password: str):
        """
        Set password for user
        This method won't commit or flush
        :param password: plain password
        :return: None
        """
        self.password_hash = password_hash.hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify password
        :param password: plain password
        :return: if password match
        """
        return password_hash.verify(password, self.password_hash)

    @staticmethod
    def get_by_identity(session: Session, identity: str) -> "User|None":
        """
        Get user by identity(email or username)
        :param session: SQLAlchemy session, use to query users
        :param identity: user.email or user.username
        :return: User or None
        """
        return session.execute(
            select(User).where(or_(User.email == identity, User.username == identity))
        ).scalar_one_or_none()


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), primary_key=True
    )
    avatar_object_key: Mapped[str | None] = mapped_column(String(128))
    full_name: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[Gender | None] = mapped_column(Enum(Gender))
    phone_number: Mapped[str | None] = mapped_column(String(15), unique=True)
    bio: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="profile")
