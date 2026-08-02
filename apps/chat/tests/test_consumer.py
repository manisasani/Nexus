import pytest
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import RefreshToken

from config.asgi import application
from apps.accounts.factories import ClientFactory
from apps.projects.factories import OpenProjectFactory, ProposalFactory
from apps.contracts.services import ProposalService
from apps.chat.models import ChatRoom


@database_sync_to_async
def _create_project_and_proposal():
    project = OpenProjectFactory()
    proposal = ProposalFactory(project=project)
    return project, proposal


@database_sync_to_async
def _accept_proposal(project, proposal):
    return ProposalService.accept(proposal_id=proposal.id, actor=project.owner)


@database_sync_to_async
def _get_room(contract):
    return ChatRoom.objects.get(contract=contract)


@database_sync_to_async
def _create_stranger():
    return ClientFactory()


@database_sync_to_async
def _get_access_token(user):
    return str(RefreshToken.for_user(user).access_token)


@database_sync_to_async
def _message_exists(room, content):
    from apps.chat.models import Message
    return Message.objects.filter(room=room, content=content).exists()


@pytest.mark.django_db
@pytest.mark.asyncio
class TestChatConsumer:

    async def test_connect_with_valid_token_succeeds(self):
        project, proposal = await _create_project_and_proposal()
        contract = await _accept_proposal(project, proposal)
        room = await _get_room(contract)

        token = await _get_access_token(contract.client)
        communicator = WebsocketCommunicator(
            application, f"/ws/chat/{room.id}/?token={token}"
        )
        connected, _ = await communicator.connect()
        assert connected
        await communicator.disconnect()

    async def test_connect_without_token_rejected(self):
        project, proposal = await _create_project_and_proposal()
        contract = await _accept_proposal(project, proposal)
        room = await _get_room(contract)

        communicator = WebsocketCommunicator(application, f"/ws/chat/{room.id}/")
        connected, _ = await communicator.connect()
        assert not connected

    async def test_non_participant_rejected(self):
        project, proposal = await _create_project_and_proposal()
        contract = await _accept_proposal(project, proposal)
        room = await _get_room(contract)

        stranger = await _create_stranger()
        token = await _get_access_token(stranger)

        communicator = WebsocketCommunicator(
            application, f"/ws/chat/{room.id}/?token={token}"
        )
        connected, _ = await communicator.connect()
        assert not connected

    async def test_message_is_persisted_and_broadcast(self):
        project, proposal = await _create_project_and_proposal()
        contract = await _accept_proposal(project, proposal)
        room = await _get_room(contract)

        token = await _get_access_token(contract.client)
        communicator = WebsocketCommunicator(
            application, f"/ws/chat/{room.id}/?token={token}"
        )
        await communicator.connect()

        await communicator.send_json_to({"message": "Hello there!"})
        response = await communicator.receive_json_from()

        assert response["content"] == "Hello there!"

        exists = await _message_exists(room, "Hello there!")
        assert exists

        await communicator.disconnect()