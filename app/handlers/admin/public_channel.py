from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from app.database.db import async_session_maker
from app.keyboards.admin.subscriptions import subscriptions_menu
from app.keyboards.admin.cancel import cancel_keyboard
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService
from app.services.subscription_validator import validate_title, parse_username_or_link
from app.states.subscription import AddPublicChannelState
from app.utils.checker import is_bot_admin_in_chat

router = Router()


@router.message(F.text == "❌ Bekor qilish")
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "❗ Bekor qilinadigan jarayon yo'q.",
            reply_markup=subscriptions_menu
        )
        return

    await state.clear()
    await message.answer(
        "❌ Amal bekor qilindi.",
        reply_markup=subscriptions_menu
    )


@router.message(F.text == "📢 Ommaviy kanal")
async def add_public_channel(message: types.Message, state: FSMContext):
    await state.set_state(AddPublicChannelState.title)
    await message.answer(
        "📢 Ommaviy kanal qo'shyapsiz!\n\n"
        "<b>Kanal nomini yuboring:</b>",
        reply_markup=cancel_keyboard
    )


@router.message(AddPublicChannelState.title, F.text != "❌ Bekor qilish")
async def get_public_channel_title(message: types.Message, state: FSMContext):
    title = (message.text or "").strip()
    error = validate_title(title)

    if error:
        await message.answer(error, reply_markup=cancel_keyboard)
        return

    await state.update_data(title=title)
    await state.set_state(AddPublicChannelState.username_or_link)

    await message.answer(
        "✅ Kanal nomi saqlandi.\n\n"
        "Endi kanal <b>username</b> yoki <b>havolasini</b> yuboring.\n\n"
        "Masalan:\n"
        "<code>@mychannel</code>\n"
        "yoki\n"
        "<code>https://t.me/mychannel</code>",
        reply_markup=cancel_keyboard
    )


@router.message(AddPublicChannelState.username_or_link, F.text != "❌ Bekor qilish")
async def get_public_channel_username_or_link(message: types.Message, state: FSMContext):
    raw_value = (message.text or "").strip()
    data = await state.get_data()
    title = data["title"]

    username, invite_link = parse_username_or_link(raw_value)

    if not username:
        await message.answer(
            "❗ Ommaviy kanal uchun to‘g‘ri username yoki link yuboring.\n\n"
            "Masalan:\n"
            "<code>@mychannel</code>\n"
            "yoki\n"
            "<code>https://t.me/mychannel</code>",
            reply_markup=cancel_keyboard
        )
        return

    bot_is_admin = await is_bot_admin_in_chat(message.bot, username)

    if not bot_is_admin:
        await message.answer(
            "❗ Bot ushbu ommaviy kanalda admin emas.\n\n"
            "Iltimos, avval botni kanalga <b>admin</b> qiling, "
            "keyin qayta urinib ko‘ring.",
            reply_markup=cancel_keyboard
        )
        return

    async with async_session_maker() as session:
        repository = SubscriptionRepository(session)
        service = SubscriptionService(repository)

        result = await service.create_public_channel(
            title=title,
            raw_value=raw_value,
        )

    if not result["ok"]:
        await message.answer(
            result["message"],
            reply_markup=cancel_keyboard
        )
        return

    subscription = result["subscription"]

    await message.answer(
        f"✅ Ommaviy kanal saqlandi.\n\n"
        f"<b>Nomi:</b> {subscription.title}\n"
        f"<b>Username:</b> {subscription.chat_username}\n"
        f"<b>Havola:</b> {subscription.invite_link}",
        reply_markup=subscriptions_menu
    )

    await state.clear()