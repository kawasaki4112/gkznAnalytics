from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import User


class UserRepository(CRUDRepository[User]):
    def __init__(self):
        super().__init__(User)
    
    async def get_by_tg_id(self, tg_id: int) -> Optional[User]:
        return await self.get(tg_id=tg_id)

user_crud = UserRepository()
