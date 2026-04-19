from aiogram.fsm.state import StatesGroup, State


class AddSubscriptionState(StatesGroup):
    title = State()
    chat_username = State()
    invite_link = State()


class AddPublicChannelState(StatesGroup):
    title = State()
    username_or_link = State()


class AddPrivateChannelState(StatesGroup):
    title = State()
    forwarded_post = State()
    invite_link = State()


class AddPublicGroupState(StatesGroup):
    title = State()
    username_or_link = State()


class AddPrivateGroupState(StatesGroup):
    title = State()
    shared_chat = State()
    invite_link = State()
    
class AddExternalLinkState(StatesGroup):
    title = State()
    url = State()

class DeleteSubscriptionState(StatesGroup):
    selecting = State()
