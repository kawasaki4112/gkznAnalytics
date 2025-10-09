from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import NetPromoterScore


class NetPromoterScoreRepository(CRUDRepository[NetPromoterScore]):
    def __init__(self):
        super().__init__(NetPromoterScore)

user_crud = NetPromoterScoreRepository()
