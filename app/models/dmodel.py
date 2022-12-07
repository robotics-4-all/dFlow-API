from datetime import datetime, timedelta

from app.models.core import DateTimeModelMixin, IDModelMixin, CoreModel


class DModelBase(CoreModel):
    raw: str


class DModelInsert(DModelBase):
    user_id: int


class DModelInDB(IDModelMixin, DateTimeModelMixin, DModelBase):
    user_id: int


class DModelPublic(DModelInDB):
    pass
