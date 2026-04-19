from aiogram import Router, types

from app.keyboards.admin.subscriptions import (
    subscriptions_menu,
    add_subscription_menu,
    channel_type_menu,
    group_type_menu,
    link_type_menu
)
from app.keyboards.admin.reply import admin_menu

router = Router()


@router.message(lambda message: message.text == "📢 Majburiy obunalar")
async def subscriptions_panel(message: types.Message):
    await message.answer(
        "📢 Majburiy obunalar bo'limi",
        reply_markup=subscriptions_menu
    )


@router.message(lambda message: message.text == "➕ Obuna qo'shish")
async def add_subscription_menu_handler(message: types.Message):
    await message.answer(
        "Qaysi turdagi obuna qo'shmoqchisiz?",
        reply_markup=add_subscription_menu
    )


@router.message(lambda message: message.text == "📢 Kanal qo'shish")
async def add_channel_menu_handler(message: types.Message):
    await message.answer(
        "Qanday kanal qo'shmoqchisiz?",
        reply_markup=channel_type_menu
    )


@router.message(lambda message: message.text == "👥 Guruh qo'shish")
async def add_group_menu_handler(message: types.Message):
    await message.answer(
        "Qanday guruh qo'shmoqchisiz?",
        reply_markup=group_type_menu
    )


@router.message(lambda message: message.text == "🔗 Havola qo'shish")
async def add_link_menu_handler(message: types.Message):
    await message.answer(
        "Qanday havola qo'shmoqchisiz?",
        reply_markup=link_type_menu
    )


@router.message(lambda message: message.text == "⬅️ Qo'shish menyusi")
async def back_to_add_subscription_menu(message: types.Message):
    await message.answer(
        "Qaysi turdagi obuna qo'shmoqchisiz?",
        reply_markup=add_subscription_menu
    )


@router.message(lambda message: message.text == "⬅️ Obunalar menyusi")
async def back_to_subscriptions_menu(message: types.Message):
    await message.answer(
        "📢 Majburiy obunalar bo'limiga qaytdingiz.",
        reply_markup=subscriptions_menu
    )


@router.message(lambda message: message.text == "🏠 Admin panel")
async def back_to_admin_panel(message: types.Message):
    await message.answer(
        "👑 Admin panelga qaytdingiz.",
        reply_markup=admin_menu
    )