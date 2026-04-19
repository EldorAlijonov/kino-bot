from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from app.database.db import async_session_maker
from app.keyboards.admin.cancel import cancel_keyboard
from app.keyboards.admin.private_group_request import private_group_request_keyboard
from app.keyboards.admin.subscriptions import subscriptions_menu
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService
from app.services.subscription_validator import validate_title
from app.states.subscription import AddPrivateGroupState
from app.utils.checker import is_bot_admin_in_chat

router = Router()


@router.message(F.text == "🔒 Maxfiy guruh")
async def add_private_group(message: types.Message, state: FSMContext):
    await state.set_state(AddPrivateGroupState.title)
    await message.answer(
        "🔒 Maxfiy guruh qo'shyapsiz.\n\n"
        "<b>Guruh nomini yuboring:</b>",
        reply_markup=cancel_keyboard,
    )


@router.message(AddPrivateGroupState.title, F.text != "❌ Bekor qilish")
async def get_private_group_title(message: types.Message, state: FSMContext):
    title = (message.text or "").strip()
    error = validate_title(title)

    if error:
        await message.answer(error, reply_markup=cancel_keyboard)
        return

    await state.update_data(title=title)
    await state.set_state(AddPrivateGroupState.shared_chat)

    await message.answer(
        "✅ Guruh nomi saqlandi.\n\n"
        "Endi pastdagi tugma orqali <b>maxfiy guruhni tanlang</b>.",
        reply_markup=private_group_request_keyboard,
    )


@router.message(AddPrivateGroupState.shared_chat, F.chat_shared)
async def get_private_group_shared_chat(message: types.Message, state: FSMContext):
    chat_shared = message.chat_shared
    chat_id = chat_shared.chat_id
    group_title = chat_shared.title or "Noma'lum guruh"

    bot_is_admin = await is_bot_admin_in_chat(message.bot, chat_id)
    if not bot_is_admin:
        await message.answer(
            "❗ Bot ushbu guruhda admin emas.\n\n"
            "Iltimos, avval botni guruhga <b>admin</b> qiling, "
            "keyin guruhni qayta tanlang.",
            reply_markup=private_group_request_keyboard,
        )
        return

    await state.update_data(chat_id=chat_id, detected_title=group_title)
    await state.set_state(AddPrivateGroupState.invite_link)

    await message.answer(
        "✅ Guruh aniqlandi.\n\n"
        f"<b>Guruh:</b> {group_title}\n"
        f"<b>Chat ID:</b> <code>{chat_id}</code>\n\n"
        "Endi guruh uchun <b>invite link</b> yuboring.",
        reply_markup=cancel_keyboard,
    )


@router.message(AddPrivateGroupState.shared_chat)
async def private_group_expected_chat_shared(message: types.Message):
    await message.answer(
        "❗ Iltimos, guruhni pastdagi maxsus tugma orqali tanlang."
    )


@router.message(AddPrivateGroupState.invite_link, F.text != "❌ Bekor qilish")
async def save_private_group(message: types.Message, state: FSMContext):
    invite_link = (message.text or "").strip()
    data = await state.get_data()

    title = data.get("title")
    chat_id = data.get("chat_id")

    if not title or not chat_id:
        await state.clear()
        await message.answer(
            "❗ Ma'lumotlar topilmadi. Jarayonni boshidan boshlang.",
            reply_markup=subscriptions_menu,
        )
        return

    async with async_session_maker() as session:
        repository = SubscriptionRepository(session)
        service = SubscriptionService(repository)

        result = await service.create_private_group(
            title=title,
            chat_id=chat_id,
            invite_link=invite_link,
        )

    if not result["ok"]:
        await message.answer(result["message"], reply_markup=cancel_keyboard)
        return

    subscription = result["subscription"]

    await message.answer(
        f"✅ Maxfiy guruh saqlandi.\n\n"
        f"<b>Nomi:</b> {subscription.title}\n"
        f"<b>Chat ID:</b> <code>{subscription.chat_id}</code>\n"
        f"<b>Havola:</b> <a href=\"{subscription.invite_link}\">Guruhga o'tish</a>",
        reply_markup=subscriptions_menu,
    )

    await state.clear()