from aiogram import Router, types
from aiogram.filters import CommandStart

from app.core.config import ADMINS
from app.database.db import async_session_maker
from app.keyboards.admin.reply import admin_menu
from app.keyboards.user.subscription import subscription_check_keyboard
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name

    if user_id in ADMINS:
        await message.answer(
            f"👑 Admin panelga xush kelibsiz, <b>{full_name}</b>!",
            reply_markup=admin_menu,
        )
        return

    async with async_session_maker() as session:
        repository = SubscriptionRepository(session)
        service = SubscriptionService(repository)
        subscriptions = await service.get_active_subscriptions()

    if not subscriptions:
        await message.answer(
            f"👋 Assalomu alaykum, <b>{full_name}</b>!"
        )
        return

    telegram_subscriptions = [
        sub for sub in subscriptions
        if sub.subscription_type != "external_link"
    ]
    external_links = [
        sub for sub in subscriptions
        if sub.subscription_type == "external_link"
    ]

    buttons_data = [
        {
            "id": sub.id,
            "title": sub.title,
            "subscription_type": sub.subscription_type,
            "chat_username": sub.chat_username,
            "invite_link": sub.invite_link,
        }
        for sub in telegram_subscriptions
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

    await message.answer(
        f"👋 Assalomu alaykum, <b>{full_name}</b>!\n\n"
        f"Botdan foydalanish uchun quyidagi obunalarga a’zo bo'ling:",
        reply_markup=subscription_check_keyboard(
            buttons_data,
            extra_links=external_links_data,
        )
    )
