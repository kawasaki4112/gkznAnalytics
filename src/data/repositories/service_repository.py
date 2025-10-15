from typing import Optional



from src.data.repositories.base_repository import CRUDRepository
from src.data.models import Service

class ServiceRepository(CRUDRepository[Service]):
    def __init__(self):
        super().__init__(Service)


service_crud = ServiceRepository()
