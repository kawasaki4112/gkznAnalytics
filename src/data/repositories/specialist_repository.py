from typing import Optional

from src.data.repositories.base_repository import CRUDRepository
from src.data.models import Specialist


class SpecialistRepository(CRUDRepository[Specialist]):
    def __init__(self):
        super().__init__(Specialist)
    
    
specialist_crud = SpecialistRepository()
