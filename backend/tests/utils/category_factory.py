from sqlalchemy.orm import Session
from app.models import Category


class CategoryFactory:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, name: str = "New Category") -> Category:
        category = Category(name=name)
        self.db_session.add(category)
        self.db_session.commit()
        return category

    def create_many(self, n: int, name_prefix: str = "CategoryName_") -> list[Category]:
        categories = [Category(name=f"{name_prefix}_{_}") for _ in range(n)]
        for category in categories:
            self.db_session.add(category)
        self.db_session.commit()
        return categories
