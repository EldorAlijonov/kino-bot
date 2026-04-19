from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from app.core.config import ADMINS
from app.database.db import async_session_maker
from app.keyboards.user.subscription import subscription_check_keyboard
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        chat = getattr(event, "chat", None)

        if user is None:
            return await handler(event, data)

        # Faqat private chatlarda ishlaydi
        if chat is not None and getattr(chat, "type", None) != "private":
            return await handler(event, data)

        if user.id in ADMINS:
            return await handler(event, data)

        if isinstance(event, CallbackQuery) and event.data == "check_subscriptions":
            return await handler(event, data)

        async with async_session_maker() as session:
            repository = SubscriptionRepository(session)
            service = SubscriptionService(repository)
            subscriptions = await service.get_active_subscriptions()

            if not subscriptions:
                return await handler(event, data)

            telegram_subscriptions = [
                sub for sub in subscriptions
                if sub.subscription_type != "external_link"
            ]
            external_links = [
                sub for sub in subscriptions
                if sub.subscription_type == "external_link"
            ]

            unsubscribed_channels = await service.get_unsubscribed_channels(
                bot=data["bot"],
                user_id=user.id,
                subscriptions=telegram_subscriptions,
            )

        if not unsubscribed_channels:
            return await handler(event, data)

        buttons_data = [
            {
                "id": sub.id,
                "title": sub.title,
                "subscription_type": sub.subscription_type,
                "chat_username": sub.chat_username,
                "invite_link": sub.invite_link,
            }
            for sub in unsubscribed_channels
        ]
        external_links_data = [
            {
                "id": sub.id,
                "title": sub.title,
                "subscription_type": sub.subscription_type,
                "chat_username": sub.chat_username,
                "invite_link": sub.invite_link,
            }
            for sub in external_links
        ]

        text = (
            "❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n\n"
            "Obuna bo‘lgach, qayta tekshiring."
        )

        if isinstance(event, Message):
            await event.answer(
                text,
                reply_markup=subscription_check_keyboard(
                    buttons_data,
                    extra_links=external_links_data,
                )
            )
            return

        if isinstance(event, CallbackQuery):
            await event.message.answer(
                text,
                reply_markup=subscription_check_keyboard(
                    buttons_data,
                    extra_links=external_links_data,
                )
            )
            await event.answer(
                "Avval majburiy obunalarga a’zo bo‘ling.",
                show_alert=True,
            )
            return

        return await handler(event, data)
