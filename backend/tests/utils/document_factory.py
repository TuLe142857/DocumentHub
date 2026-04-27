from typing import Literal

from sqlalchemy.orm import Session

from app.models import Document, User, DocumentStatus, DocumentVisibility, Category


class DocumentFactory:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(
        self,
        owner: User,
        category: Category,
        title: str = "DocumentName",
        desc: str = "DocumentDescription",
        visibility: DocumentVisibility = DocumentVisibility.PUBLIC,
        file_type: Literal[".doc", ".docx", ".pdf", ".ppt", ".pptx"] = ".doc",
        status: DocumentStatus = DocumentStatus.READY,
    ) -> Document:
        doc = Document(
            title=title,
            desc=desc,
            category=category,
            owner=owner,
            visibility=visibility,
            file_type=file_type,
            file_preview_object_key="file_preview_object_key_pub",
            file_object_key="file_object_key_pub",
            sha256sum="sha256sum",
            md5sum="md5sum",
            status=status,
            thumbnail_object_key="thumbnail_object_key",
        )
        self.db_session.add(doc)
        self.db_session.commit()
        return doc

    def create_many(
        self,
        n: int,
        owner: User,
        category: Category,
        title_prefix: str = "DocumentTitle_",
    ) -> list[Document]:
        docs = [
            Document(
                title=f"{title_prefix}{_}",
                desc="Test Document Description",
                category=category,
                owner=owner,
                visibility=DocumentVisibility.PUBLIC,
                file_type=".doc",
                file_preview_object_key="file_preview_object_key_pub",
                file_object_key="file_object_key_pub",
                sha256sum="sha256sum",
                md5sum="md5sum",
                status=DocumentStatus.READY,
                thumbnail_object_key="thumbnail_object_key",
            )
            for _ in range(n)
        ]
        for doc in docs:
            self.db_session.add(doc)
        self.db_session.commit()
        return docs
