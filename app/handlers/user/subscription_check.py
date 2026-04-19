from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.database.db import async_session_maker
from app.keyboards.user.subscription import subscription_check_keyboard
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService

router = Router()


@router.callback_query(F.data == "check_subscriptions")
async def check_subscriptions(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with async_session_maker() as session:
        repository = SubscriptionRepository(session)
        service = SubscriptionService(repository)

        subscriptions = await service.get_active_subscriptions()
        telegram_subscriptions = [
            sub for sub in subscriptions
            if sub.subscription_type != "external_link"
        ]
        external_links = [
            sub for sub in subscriptions
            if sub.subscription_type == "external_link"
        ]

        unsubscribed_channels = await service.get_unsubscribed_channels(
            bot=callback.bot,
            user_id=user_id,
            subscriptions=telegram_subscriptions,
        )

    if not unsubscribed_channels:
        try:
            await callback.message.edit_text(
                "✅ Barcha majburiy obunalar bajarilgan. Kino kodini yuboring."
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise

        await callback.answer()
        return

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
        "❗ Siz hali quyidagi obunalarga ulanmagansiz.\n\n"
        "Iltimos, obuna bo‘lib qayta tekshiring:"
    )

    try:
        await callback.message.edit_text(
            text,
            reply_markup=subscription_check_keyboard(
                buttons_data,
                extra_links=external_links_data,
            ),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

    await callback.answer()
