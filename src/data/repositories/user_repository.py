from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import User


class UserRepository(CRUDRepository[User]):
    def __init__(self):
        super().__init__(User)


user_crud = UserRepository()
