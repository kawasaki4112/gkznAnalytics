from typing import Optional, List
from sqlalchemy import select, distinct

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import Specialist
from src.data.db import async_session


class SpecialistRepository(CRUDRepository[Specialist]):
    def __init__(self):
        super().__init__(Specialist)
    
    async def get_unique_organizations(self) -> List[str]:
        """
        Возвращает список уникальных организаций.
        """
        async with async_session() as session:
            stmt = select(distinct(Specialist.organization)).order_by(Specialist.organization)
            result = await session.execute(stmt)
            return [org for org in result.scalars().all() if org]
    
    
specialist_crud = SpecialistRepository()
