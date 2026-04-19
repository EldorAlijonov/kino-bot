from sqlalchemy.exc import IntegrityError

from app.services.subscription_validator import (
    parse_username_or_link,
    validate_public_channel_data,
    validate_private_invite_link,
    validate_title,
    is_valid_external_url,
)
from app.utils.checker import is_user_subscribed


class SubscriptionService:
    def __init__(self, repository):
        self.repository = repository

    # ======================
    # CHANNEL
    # ======================

    async def create_public_channel(self, title: str, raw_value: str):
        username, invite_link = parse_username_or_link(raw_value)

        error = validate_public_channel_data(title, username, invite_link)
        if error:
            return {"ok": False, "message": error}

        exists = await self.repository.exists_by_username(username)
        if exists:
            return {"ok": False, "message": "❗ Bu ommaviy kanal oldin qo'shilgan."}

        try:
            subscription = await self.repository.create_public_channel(
                title=title,
                chat_username=username,
                invite_link=invite_link,
            )
        except IntegrityError:
            return {"ok": False, "message": "❗ Bu ommaviy kanal oldin qo'shilgan."}

        return {"ok": True, "subscription": subscription}

    async def create_private_channel(
        self,
        title: str,
        chat_id: int,
        invite_link: str,
    ):
        title_error = validate_title(title)
        if title_error:
            return {"ok": False, "message": title_error}

        invite_link_error = validate_private_invite_link(invite_link)
        if invite_link_error:
            return {"ok": False, "message": invite_link_error}

        exists = await self.repository.exists_by_chat_id(chat_id)
        if exists:
            return {"ok": False, "message": "❗ Bu maxfiy kanal oldin qo'shilgan."}

        try:
            subscription = await self.repository.create_private_channel(
                title=title,
                chat_id=chat_id,
                invite_link=invite_link,
            )
        except IntegrityError:
            return {"ok": False, "message": "❗ Bu maxfiy kanal oldin qo'shilgan."}

        return {"ok": True, "subscription": subscription}

    # ======================
    # GROUP
    # ======================

    async def create_public_group(self, title: str, raw_value: str):
        username, invite_link = parse_username_or_link(raw_value)

        error = validate_public_channel_data(title, username, invite_link)
        if error:
            return {"ok": False, "message": error}

        exists = await self.repository.exists_by_username(username)
        if exists:
            return {"ok": False, "message": "❗ Bu guruh oldin qo'shilgan."}

        try:
            subscription = await self.repository.create_public_group(
                title=title,
                chat_username=username,
                invite_link=invite_link,
            )
        except IntegrityError:
            return {"ok": False, "message": "❗ Bu guruh oldin qo'shilgan."}

        return {"ok": True, "subscription": subscription}

    async def create_private_group(
        self,
        title: str,
        chat_id: int,
        invite_link: str,
    ):
        title_error = validate_title(title)
        if title_error:
            return {"ok": False, "message": title_error}

        invite_link_error = validate_private_invite_link(invite_link)
        if invite_link_error:
            return {"ok": False, "message": invite_link_error}

        exists = await self.repository.exists_by_chat_id(chat_id)
        if exists:
            return {"ok": False, "message": "❗ Bu guruh oldin qo'shilgan."}

        try:
            subscription = await self.repository.create_private_group(
                title=title,
                chat_id=chat_id,
                invite_link=invite_link,
            )
        except IntegrityError:
            return {"ok": False, "message": "❗ Bu guruh oldin qo'shilgan."}

        return {"ok": True, "subscription": subscription}

    # ======================
    # LINK
    # ======================

    async def create_external_link(self, title: str, url: str):
        title_error = validate_title(title)
        if title_error:
            return {"ok": False, "message": title_error}

        if not is_valid_external_url(url):
            return {"ok": False, "message": "❗ Havola noto‘g‘ri formatda."}

        try:
            subscription = await self.repository.create_external_link(
                title=title,
                invite_link=url,
            )
        except IntegrityError:
            return {"ok": False, "message": "❗ Bu havola oldin qo'shilgan."}

        return {"ok": True, "subscription": subscription}

    # ======================
    # LIST
    # ======================

    async def get_active_subscriptions(self):
        return await self.repository.get_active()

    async def get_all_subscriptions(self):
        return await self.repository.get_all()

    async def get_paginated_subscriptions(self, limit: int, offset: int):
        return await self.repository.get_all_paginated(
            limit=limit,
            offset=offset,
        )

    async def count_all_subscriptions(self) -> int:
        return await self.repository.count_all()

    async def get_unsubscribed_channels(self, bot, user_id: int, subscriptions):
        unsubscribed = []

        for sub in subscriptions:
            if sub.subscription_type == "external_link":
                continue

            chat_identifier = sub.chat_username if sub.chat_username else sub.chat_id

            if not chat_identifier:
                continue

            is_subscribed = await is_user_subscribed(
                bot,
                chat_identifier,
                user_id,
            )

            if not is_subscribed:
                unsubscribed.append(sub)

        return unsubscribed

    # ======================
    # DELETE
    # ======================

    async def delete_subscription(self, subscription_id: int) -> bool:
        subscription = await self.repository.get_by_id(subscription_id)
        if not subscription:
            return False

        return await self.repository.delete_by_id(subscription_id)
