from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.database.models.subscription import Subscription


class SubscriptionRepository:
    def __init__(self, session):
        self.session = session

    async def create_public_channel(
        self,
        title: str,
        chat_username: str,
        invite_link: str,
    ) -> Subscription:
        subscription = Subscription(
            title=title,
            subscription_type="public_channel",
            chat_username=chat_username,
            invite_link=invite_link,
            is_active=True,
        )

        self.session.add(subscription)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(subscription)
        return subscription

    async def create_private_channel(
        self,
        title: str,
        chat_id: int,
        invite_link: str,
    ) -> Subscription:
        subscription = Subscription(
            title=title,
            subscription_type="private_channel",
            chat_id=chat_id,
            invite_link=invite_link,
            is_active=True,
        )

        self.session.add(subscription)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(subscription)
        return subscription

    async def create_public_group(
        self,
        title: str,
        chat_username: str,
        invite_link: str,
    ) -> Subscription:
        subscription = Subscription(
            title=title,
            subscription_type="public_group",
            chat_username=chat_username,
            invite_link=invite_link,
            is_active=True,
        )

        self.session.add(subscription)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(subscription)
        return subscription

    async def create_private_group(
        self,
        title: str,
        chat_id: int,
        invite_link: str,
    ) -> Subscription:
        subscription = Subscription(
            title=title,
            subscription_type="private_group",
            chat_id=chat_id,
            invite_link=invite_link,
            is_active=True,
        )

        self.session.add(subscription)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(subscription)
        return subscription

    async def create_external_link(
        self,
        title: str,
        invite_link: str,
    ) -> Subscription:
        subscription = Subscription(
            title=title,
            subscription_type="external_link",
            invite_link=invite_link,
            is_active=True,
        )

        self.session.add(subscription)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(subscription)
        return subscription

    async def get_by_username(self, chat_username: str) -> Subscription | None:
        result = await self.session.execute(
            select(Subscription).where(Subscription.chat_username == chat_username)
        )
        return result.scalar_one_or_none()

    async def exists_by_username(self, chat_username: str) -> bool:
        subscription = await self.get_by_username(chat_username)
        return subscription is not None

    async def get_by_chat_id(self, chat_id: int) -> Subscription | None:
        result = await self.session.execute(
            select(Subscription).where(Subscription.chat_id == chat_id)
        )
        return result.scalar_one_or_none()

    async def exists_by_chat_id(self, chat_id: int) -> bool:
        subscription = await self.get_by_chat_id(chat_id)
        return subscription is not None

    async def get_active(self) -> list[Subscription]:
        result = await self.session.execute(
            select(Subscription).where(Subscription.is_active.is_(True))
        )
        return result.scalars().all()

    async def get_all(self) -> list[Subscription]:
        result = await self.session.execute(
            select(Subscription).order_by(Subscription.id.desc())
        )
        return result.scalars().all()

    async def get_all_paginated(self, limit: int, offset: int):
        result = await self.session.execute(
            select(Subscription)
            .order_by(Subscription.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def count_all(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Subscription)
        )
        return result.scalar_one()

    async def get_by_id(self, subscription_id: int) -> Subscription | None:
        result = await self.session.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()

    async def delete_by_id(self, subscription_id: int) -> bool:
        subscription = await self.get_by_id(subscription_id)
        if not subscription:
            return False

        await self.session.delete(subscription)
        await self.session.commit()
        return True