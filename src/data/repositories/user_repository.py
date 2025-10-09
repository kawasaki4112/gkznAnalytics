from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import User


class UserRepository(CRUDRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_tg_id(self, tg_id: int) -> Optional[User]:
        return await self.get(tg_id=tg_id)

    async def update_balance(self, tg_id: int, sum: float, operation: str) -> Optional[User]:
        user = await self.get_by_tg_id(tg_id)
        if user:
            if operation == 'add':
                user.balance += sum
            elif operation == 'subtract':
                user.balance -= sum
            else:
                raise ValueError("Operation must be 'add' or 'subtract'")
            await self.update(user)
        return user

user_crud = UserRepository()
