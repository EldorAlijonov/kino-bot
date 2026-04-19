import math

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions

from app.database.db import async_session_maker
from app.keyboards.admin.subscription_list_inline import subscription_list_navigation_keyboard
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService

router = Router()

PAGE_SIZE = 5


async def build_subscription_list_text(page: int):
    offset = (page - 1) * PAGE_SIZE

    async with async_session_maker() as session:
        repository = SubscriptionRepository(session)
        service = SubscriptionService(repository)

        total_count = await service.count_all_subscriptions()
        subscriptions = await service.get_paginated_subscriptions(
            limit=PAGE_SIZE,
            offset=offset
        )

    if total_count == 0:
        return None, None

    total_pages = math.ceil(total_count / PAGE_SIZE)

    lines = [
        f"📋 <b>Obunalar ro‘yxati</b>\n"
        f"📄 Sahifa: {page}/{total_pages}\n"
    ]

    subscription_type_labels = {
        "public_channel": "Ommaviy kanal",
        "private_channel": "Maxfiy kanal",
        "public_group": "Ommaviy guruh",
        "private_group": "Maxfiy guruh",
        "external_link": "Oddiy havola",
    }

    for index, sub in enumerate(subscriptions, start=offset + 1):
        status = "✅ Aktiv" if sub.is_active else "❌ Nofaol"
        subscription_type_label = subscription_type_labels.get(
            sub.subscription_type,
            "Noma'lum"
        )

        if sub.subscription_type in ("public_channel", "public_group"):
            address_line = sub.chat_username or "-"
        else:
            address_line = f'<a href="{sub.invite_link}">🔗 Ochish</a>'

        lines.append(
            f"{index}. Obuna nomi:<b> {sub.title}</b>\n"
            f"• ID: <code>{sub.id}</code>\n"
            f"• Turi: {subscription_type_label}\n"
            f"• Manzil: {address_line}\n"
            f"• Holati: {status}\n"
        )

    return "\n".join(lines), subscription_list_navigation_keyboard(page, total_pages)


@router.message(F.text == "📋 Obunalar ro'yxati")
async def show_subscription_list(message: Message):
    text, keyboard = await build_subscription_list_text(page=1)

    if not text:
        await message.answer("📭 Hozircha obunalar yo‘q.")
        return

    await message.answer(
        text,
        reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )


@router.callback_query(F.data.startswith("subscription_list:"))
async def paginate_subscription_list(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])

    text, keyboard = await build_subscription_list_text(page=page)

    if not text:
        await callback.answer("❗ Ma'lumot topilmadi.")
        return

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    await callback.answer()