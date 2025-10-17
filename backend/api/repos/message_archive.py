from .base_repository import BaseRepository
from api.models import MessageArchived

class MessageRepo(BaseRepository):
    
    def __init__(self):
        super().__init__(MessageArchived)