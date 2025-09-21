from django.db import models
from django.contrib.auth import get_user_model
import uuid
User = get_user_model()


ROLE_CHOICE = [
    ('user', 'User'),
    ('assistant', 'Assistant'),
]

MESSAGE_STATUS = [
    ('pending', 'Pending'),
    ('sent', 'Sent'),
    ('failed', 'Failed'),
]
class UUIDTimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    class Meta:
        abstract = True 
class Conversation(UUIDTimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=350)

    def __str__(self):
        return f'{self.user} - {self.title}'

class BaseMessage(UUIDTimeStampedModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    content = models.TextField()
    role = models.CharField(choices=ROLE_CHOICE, max_length=150)
    payload = models.JSONField(blank=True, null=True)
    usage = models.JSONField(blank=True, null=True)
    status = models.CharField(choices=MESSAGE_STATUS, max_length=150)
    position = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
class Messages(BaseMessage):
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

class MessageArchived(BaseMessage):
    class Meta:
        db_table = 'archived_messages'