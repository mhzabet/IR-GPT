import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

from IRGPT.asgi import application

User = get_user_model()

@database_sync_to_async
def create_test_user():
    return User.objects.create_user(
        username="testuser",
        email="test@mail.com",
        password="Password@123",
        is_active=True
    )

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_chat_consumer():

    user = await create_test_user()
    communicator = WebsocketCommunicator(
        application,
        "ws/chat/"
    )
    communicator.scope['user'] = user

    # Connect 
    connected, subprotocol = await communicator.connect()
    print("Connected?", connected)  # debug output

    assert connected
    
     # 4. Send message
    await communicator.send_json_to({"message": "Hello IR-GPT"})

    # 5. Receive echoed message
    response = await communicator.receive_json_from()
    assert response["message"]

    # 6. Close
    await communicator.disconnect()