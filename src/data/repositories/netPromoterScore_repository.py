from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.data.repositories.base_repository import CRUDRepository, async_session
from src.data.models import NetPromoterScore, AssessmentOfQuality


class NetPromoterScoreRepository(CRUDRepository[NetPromoterScore]):
    def __init__(self):
        super().__init__(NetPromoterScore)

    async def get_list_with_relations(self):
        async with async_session() as session:
            stmt = select(NetPromoterScore)
            stmt = stmt.options(
                selectinload(NetPromoterScore.user),
                selectinload(NetPromoterScore.aoq).selectinload(AssessmentOfQuality.specialist),
            )
            result = await session.execute(stmt)
            return result.scalars().all()
    
nps_crud = NetPromoterScoreRepository()
