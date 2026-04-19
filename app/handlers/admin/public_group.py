from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from app.database.db import async_session_maker
from app.keyboards.admin.subscriptions import subscriptions_menu
from app.keyboards.admin.cancel import cancel_keyboard
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService
from app.services.subscription_validator import validate_title, parse_username_or_link
from app.states.subscription import AddPublicGroupState
from app.utils.checker import is_bot_admin_in_chat

router = Router()


@router.message(F.text == "👥 Ommaviy guruh")
async def add_public_group(message: types.Message, state: FSMContext):
    await state.set_state(AddPublicGroupState.title)
    await message.answer("👥 Guruh nomini yuboring:", reply_markup=cancel_keyboard)


@router.message(AddPublicGroupState.title)
async def get_title(message: types.Message, state: FSMContext):
    title = message.text.strip()

    error = validate_title(title)
    if error:
        await message.answer(error)
        return

    await state.update_data(title=title)
    await state.set_state(AddPublicGroupState.username_or_link)

    await message.answer("Guruh username yoki link yuboring:")


@router.message(AddPublicGroupState.username_or_link)
async def get_group(message: types.Message, state: FSMContext):
    raw = message.text.strip()
    data = await state.get_data()

    username, _ = parse_username_or_link(raw)

    if not username:
        await message.answer("❗ Username noto‘g‘ri")
        return
    chat = await message.bot.get_chat(username)

    if not await is_bot_admin_in_chat(message.bot, username):
        await message.answer("❗ Bot guruhda admin emas")
        return

    async with async_session_maker() as session:
        service = SubscriptionService(SubscriptionRepository(session))

        result = await service.create_public_group(
            title=data["title"],
            raw_value=raw,
        )

    if not result["ok"]:
        await message.answer(result["message"])
        return

    await message.answer("✅ Guruh saqlandi", reply_markup=subscriptions_menu)
    await state.clear()