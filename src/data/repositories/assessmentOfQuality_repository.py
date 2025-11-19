from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.data.repositories.base_repository import CRUDRepository, async_session
from src.data.models import AssessmentOfQuality, User


class AssessmentOfQualityRepository(CRUDRepository[AssessmentOfQuality]):
    def __init__(self):
        super().__init__(AssessmentOfQuality)

    async def get_list_with_relations(self):
        async with async_session() as session:
            stmt = select(AssessmentOfQuality)
            stmt = stmt.options(
                selectinload(AssessmentOfQuality.user).selectinload(User.socialsubcategory),
                selectinload(AssessmentOfQuality.specialist),
                selectinload(AssessmentOfQuality.service),
            )
            result = await session.execute(stmt)
            return result.scalars().all()
        
aoq_crud = AssessmentOfQualityRepository()
