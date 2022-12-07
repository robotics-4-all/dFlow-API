from app.db.repositories.base import BaseRepository

from app.models.dmodel import DModelInsert, DModelInDB, DModelPublic


ADD_MODEL_FOR_USER_QUERY = """
    INSERT INTO models (raw, user_id)
    VALUES (:raw, :user_id)
    RETURNING id, raw, user_id, created_at, updated_at;
"""

GET_MODEL_BY_ID_QUERY = """
    SELECT id, raw, user_id, created_at, updated_at
    FROM models
    WHERE id = :id;
"""

GET_MODEL_BY_USER_ID_QUERY = """
    SELECT id, raw, user_id, created_at, updated_at
    FROM models
    WHERE user_id = :user_id;
"""

GET_MODEL_BY_USERNAME_QUERY = """
    SELECT m.id,
           raw,
           user_id,
           m.created_at,
           m.updated_at
    FROM models m
        INNER JOIN users u
        ON m.user_id = u.id
    WHERE user_id = (SELECT id FROM users WHERE username = :username);
"""

GET_LAST_MODEL_FOR_USER_QUERY = """
    SELECT m.id,
           raw,
           user_id,
           m.created_at,
           m.updated_at
    FROM models m
        INNER JOIN users u
        ON m.user_id = u.id
    WHERE user_id = (SELECT id FROM users WHERE username = :username)
    ORDER BY (updated_at) DESC LIMIT 1;
"""


class DModelRepository(BaseRepository):
    async def add_model_for_user(self,
                                 *,
                                 user_id: str,
                                 model_raw: str
                                 ) -> DModelInDB:
        m = DModelInsert(user_id=user_id, raw=model_raw)
        dmodel = await self.db.fetch_one(
            query=ADD_MODEL_FOR_USER_QUERY,
            values=m.dict()
        )

        return dmodel

    async def get_model_by_id(self,
                              *,
                              model_id: int) -> DModelInDB:
        dmodel = await self.db.fetch_one(
            query=GET_MODEL_BY_ID_QUERY,
            values={"id": model_id}
        )

        if not dmodel:
            return None

        return DModelInDB(**dmodel)

    async def get_models_for_user(self,
                                  *,
                                  username: str) -> DModelInDB:
        dmodel = await self.db.fetch_one(
            query=GET_MODEL_BY_USERNAME_QUERY,
            values={"username": username})

        if dmodel:
            return DModelInDB(**dmodel)
        return dmodel

    async def get_last_model_for_user(self,
                                      *,
                                      username: str) -> DModelInDB:
        dmodel = await self.db.fetch_one(
            query=GET_LAST_MODEL_FOR_USER_QUERY,
            values={"username": username})

        if dmodel:
            return DModelInDB(**dmodel)
        return dmodel
