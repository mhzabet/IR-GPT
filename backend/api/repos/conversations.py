from .base_repository import BaseRepository
from api.models import Conversation

class ConversationRepo(BaseRepository):
    def __init__(self):
        super().__init__(Conversation)