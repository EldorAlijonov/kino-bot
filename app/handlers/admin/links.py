from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from app.database.db import async_session_maker
from app.repositories.subscription_repository import SubscriptionRepository
from app.services.subscription_service import SubscriptionService
from app.states.subscription import AddExternalLinkState
from app.keyboards.admin.cancel import cancel_keyboard

router = Router()


@router.message(F.text == "🔗 Havola qo'shish")
async def ask_link_type(message: types.Message):
    await message.answer("Qanday havola qo'shmoqchisiz?")


@router.message(F.text == "🔗 Oddiy havola")
async def start_add_external_link(message: types.Message, state: FSMContext):
    await state.set_state(AddExternalLinkState.title)
    await message.answer(
        "Havola nomini yuboring:",
        reply_markup=cancel_keyboard
    )


@router.message(AddExternalLinkState.title)
async def get_external_link_title(message: types.Message, state: FSMContext):
    title = message.text.strip()

    if not title:
        await message.answer(
            "❗ Havola nomi bo‘sh bo‘lmasligi kerak",
            reply_markup=cancel_keyboard
        )
        return

    await state.update_data(title=title)
    await state.set_state(AddExternalLinkState.url)
    await message.answer(
        "Havolani yuboring:\n\n"
        "Masalan:\n"
        "https://example.com",
        reply_markup=cancel_keyboard
    )


@router.message(AddExternalLinkState.url)
async def get_external_link_url(message: types.Message, state: FSMContext):
    url = message.text.strip()
    data = await state.get_data()
    title = data.get("title")

    async with async_session_maker() as session:
        repository = SubscriptionRepository(session)
        service = SubscriptionService(repository)

        try:
            result = await service.create_external_link(
                title=title,
                url=url,
            )
        except Exception as e:
            print("EXTERNAL LINK SAVE ERROR:", e)
            await message.answer(
                "❗ Havolani saqlashda xatolik yuz berdi",
                reply_markup=cancel_keyboard
            )
            return

    if not result["ok"]:
        await message.answer(
            result["message"],
            reply_markup=cancel_keyboard
        )
        return

    subscription = result["subscription"]

    await state.clear()
    await message.answer(
        f"✅ Havola qo‘shildi\n\n"
        f"Obuna nomi: <b>{subscription.title}</b>\n"
        f"Turi: Oddiy havola\n"
        f"Havola: {subscription.invite_link}"
    )