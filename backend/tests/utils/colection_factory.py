from sqlalchemy.orm import Session

from app.models import User, Collection, CollectionItem, Document


class CollectionFactory:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(
        self,
        owner: User,
        name: str = "CollectionName",
        items: list[Document] | None = None,
    ) -> Collection:
        collection = Collection(owner=owner, name=name)
        if items is not None:
            collection.items = [CollectionItem(document=item) for item in items]
        self.db_session.add(collection)
        self.db_session.commit()
        return collection

    def create_many(
        self, n: int, owner: User, name_prefix: str = "CollectionName_"
    ) -> list[Collection]:
        """
        Create a list of collections
        Args:
            n: number of collections to create
            owner:
            name_prefix: name prefix for all collections name. Example: name_prefix="col", n=3. Collection name
                will be: ["col0", "col1", "col2"]

        Returns:

        """
        collections = [
            Collection(owner=owner, name=f"{name_prefix}{_}") for _ in range(n)
        ]
        for collection in collections:
            self.db_session.add(collection)
        self.db_session.commit()
        return collections
