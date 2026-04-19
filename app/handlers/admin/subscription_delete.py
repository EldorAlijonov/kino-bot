import math

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions

from app.database.db import async_session_maker
from app.keyboards.admin.cancel import cancel_keyboard
from app.keyboards.admin.subscription_delete_inline import subscription_delete_keyboard
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService
from app.states.subscription import DeleteSubscriptionState

router = Router()

PAGE_SIZE = 5


def build_subscription_type_label(subscription_type: str) -> str:
    type_labels = {
        "public_channel": "Ommaviy kanal",
        "private_channel": "Maxfiy kanal",
        "public_group": "Ommaviy guruh",
        "private_group": "Maxfiy guruh",
    }
    return type_labels.get(subscription_type, "Noma'lum")


async def build_delete_list_text(page: int):
    async with async_session_maker() as session:
        repository = SubscriptionRepository(session)
        service = SubscriptionService(repository)

        total_count = await service.count_all_subscriptions()

        if total_count == 0:
            return None, None, 0

        total_pages = math.ceil(total_count / PAGE_SIZE)

        if page > total_pages:
            page = total_pages

        offset = (page - 1) * PAGE_SIZE
        subscriptions = await service.get_paginated_subscriptions(
            limit=PAGE_SIZE,
            offset=offset
        )

    lines = [
        "🗑 <b>O‘chirish uchun obunani tanlang</b>",
        f"📄 Sahifa: {page}/{total_pages}",
        ""
    ]

    for index, sub in enumerate(subscriptions, start=1):
        status = "✅ Aktiv" if sub.is_active else "❌ Nofaol"
        subscription_type_label = build_subscription_type_label(sub.subscription_type)

        if sub.subscription_type in ("public_channel", "public_group"):
            address_line = sub.chat_username or "-"
        else:
            address_line = f'<a href="{sub.invite_link}">🔗 Ochish</a>'

        lines.append(
            f"{index}. Obuna nomi: <b>{sub.title}</b>\n"
            f"• ID: <code>{sub.id}</code>\n"
            f"• Turi: {subscription_type_label}\n"
            f"• Manzil: {address_line}\n"
            f"• Holati: {status}\n"
        )

    keyboard = subscription_delete_keyboard(
        subscriptions=subscriptions,
        page=page,
        total_pages=total_pages
    )

    return "\n".join(lines), keyboard, page


@router.message(F.text == "🗑 O'chirish")
async def show_delete_list(message: Message, state: FSMContext):
    text, keyboard, _ = await build_delete_list_text(page=1)

    if not text:
        await state.clear()
        await message.answer("📭 Hozircha obunalar yo‘q.")
        return

    await state.set_state(DeleteSubscriptionState.selecting)

    await message.answer(
        text,
        reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    await message.answer(
        "❌ Bekor qilish tugmasi orqali ortga qaytishingiz mumkin.",
        reply_markup=cancel_keyboard
    )


@router.callback_query(DeleteSubscriptionState.selecting, F.data.startswith("delete_subscription_page:"))
async def paginate_delete_list(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])

    text, keyboard, _ = await build_delete_list_text(page=page)

    if not text:
        await callback.answer("📭 Hozircha obunalar yo‘q.", show_alert=True)
        await callback.message.edit_text("📭 Hozircha obunalar yo‘q.")
        return

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    await callback.answer()


@router.callback_query(DeleteSubscriptionState.selecting, F.data == "delete_subscription_current_page")
async def keep_delete_page(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(DeleteSubscriptionState.selecting, F.data.startswith("delete_subscription:"))
async def delete_subscription_handler(callback: CallbackQuery, state: FSMContext):
    _, subscription_id_str, page_str = callback.data.split(":")
    subscription_id = int(subscription_id_str)
    page = int(page_str)

    async with async_session_maker() as session:
        repository = SubscriptionRepository(session)
        service = SubscriptionService(repository)
        deleted = await service.delete_subscription(subscription_id)

    if not deleted:
        await callback.answer("❗ Obuna topilmadi", show_alert=True)
        return

    text, keyboard, actual_page = await build_delete_list_text(page=page)

    if not text:
        await state.clear()
        await callback.message.edit_text("✅ Barcha obunalar o‘chirildi.")
        await callback.answer("✅ Obuna o‘chirildi")
        return

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    await callback.answer(f"✅ Obuna o‘chirildi. Sahifa: {actual_page}")
