from django.test import TestCase
from api.models import Conversation, Messages, MessageArchived
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()

class TestConversationModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'testUser', 'test@mail.com', 'TestPassword123!', is_active=True
        )
        self.conv = Conversation.objects.create(title="Test Conversation", user=self.user)
    def test_conversation_model(self):
        self.assertEqual(Conversation.objects.count(), 1)

class TestMessagesModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'testUser', 'test@mail.com', 'TestPassword123!',
            is_active=True
        )

        # Create conversation
        self.conv = Conversation.objects.create(
            title="Test Conversation",
            user=self.user
        )

        # Create a message
        self.msg = Messages.objects.create(
            conversation=self.conv,
            content="Test Message by user",
            role='user',
            payload={'intent':'greeting'},
            status='pending',
            usage={'tokens':10},
            position=1
        )

    def test_messages_model(self):
        self.assertEqual(Messages.objects.count(), 1)
    def test_archived_messages(self):
        archived_msg = MessageArchived.objects.create(
            conversation=self.msg.conversation,
            content=self.msg.content,
            role=self.msg.role,
            payload=self.msg.payload,
            status=self.msg.status,
            usage=self.msg.usage,
            position=self.msg.position,
            archived_at=timezone.now()
        )
        self.assertEqual(MessageArchived.objects.count(), 1)

