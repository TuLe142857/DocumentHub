from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.dependencies import DBSessionDep
from app.models import DocumentReport

from .base import CRUDBase


class CRUDReport(CRUDBase[DocumentReport, BaseModel, BaseModel]):
    def __init__(self, db_session: Session):
        super().__init__(DocumentReport, db_session)


def get_crud_report(db_session: DBSessionDep) -> CRUDReport:
    return CRUDReport(db_session)


CRUDReportDep = Annotated[CRUDReport, Depends(get_crud_report)]
