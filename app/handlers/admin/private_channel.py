from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from app.database.db import async_session_maker
from app.keyboards.admin.cancel import cancel_keyboard
from app.keyboards.admin.subscriptions import subscriptions_menu
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService
from app.services.subscription_validator import validate_title
from app.states.subscription import AddPrivateChannelState
from app.utils.checker import is_bot_admin_in_chat

router = Router()


def extract_forwarded_chat_id(message: types.Message) -> int | None:
    if message.forward_origin and hasattr(message.forward_origin, "chat"):
        chat = message.forward_origin.chat
        if chat:
            return chat.id

    if message.forward_from_chat:
        return message.forward_from_chat.id

    return None


@router.message(F.text == "🔒 Maxfiy kanal")
async def add_private_channel(message: types.Message, state: FSMContext):
    await state.set_state(AddPrivateChannelState.title)
    await message.answer(
        "🔒 Maxfiy kanal qo'shyapsiz.\n\n"
        "<b>Kanal nomini yuboring:</b>",
        reply_markup=cancel_keyboard,
    )


@router.message(AddPrivateChannelState.title, F.text != "❌ Bekor qilish")
async def get_private_channel_title(message: types.Message, state: FSMContext):
    title = (message.text or "").strip()
    error = validate_title(title)

    if error:
        await message.answer(
            error,
            reply_markup=cancel_keyboard,
        )
        return

    await state.update_data(title=title)
    await state.set_state(AddPrivateChannelState.forwarded_post)

    await message.answer(
        "✅ Kanal nomi saqlandi.\n\n"
        "Endi botni <b>maxfiy kanalga admin</b> qiling va "
        "shu kanaldan <b>ixtiyoriy postni forward</b> qiling.",
        reply_markup=cancel_keyboard,
    )


@router.message(AddPrivateChannelState.forwarded_post, F.text != "❌ Bekor qilish")
async def get_private_channel_forwarded_post(message: types.Message, state: FSMContext):
    chat_id = extract_forwarded_chat_id(message)

    if not chat_id:
        await message.answer(
            "❗ Men kanalni aniqlay olmadim.\n\n"
            "Iltimos, <b>maxfiy kanaldan forward qilingan post</b> yuboring.",
            reply_markup=cancel_keyboard,
        )
        return

    bot_is_admin = await is_bot_admin_in_chat(message.bot, chat_id)

    if not bot_is_admin:
        await message.answer(
            "❗ Bot ushbu maxfiy kanalda admin emas.\n\n"
            "Iltimos, avval botni kanalga <b>admin</b> qiling, "
            "keyin o‘sha kanaldan postni qayta forward qiling.",
            reply_markup=cancel_keyboard,
        )
        return

    await state.update_data(chat_id=chat_id)
    await state.set_state(AddPrivateChannelState.invite_link)

    await message.answer(
        "✅ Kanal aniqlandi va bot admin ekanligi tasdiqlandi.\n\n"
        f"<b>Chat ID:</b> <code>{chat_id}</code>\n\n"
        "Endi maxfiy kanal uchun <b>invite link</b> yuboring.\n\n"
        "Masalan:\n"
        "<code>https://t.me/+abc123xyz</code>",
        reply_markup=cancel_keyboard,
    )


@router.message(AddPrivateChannelState.invite_link, F.text != "❌ Bekor qilish")
async def get_private_channel_invite_link(message: types.Message, state: FSMContext):
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

        result = await service.create_private_channel(
            title=title,
            chat_id=chat_id,
            invite_link=invite_link,
        )

    if not result["ok"]:
        await message.answer(
            result["message"],
            reply_markup=cancel_keyboard,
        )
        return

    subscription = result["subscription"]

    await message.answer(
        f"✅ Maxfiy kanal saqlandi.\n\n"
        f"<b>Nomi:</b> {subscription.title}\n"
        f"<b>Chat ID:</b> <code>{subscription.chat_id}</code>\n"
        f"<b>Havola:</b> <a href=\"{subscription.invite_link}\">Kanalga o'tish</a>",
        reply_markup=subscriptions_menu,
    )

    await state.clear()