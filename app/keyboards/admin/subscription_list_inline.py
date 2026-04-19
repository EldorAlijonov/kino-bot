from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def subscription_list_navigation_keyboard(page: int, total_pages: int):
    buttons = []

    row = []

    if page > 1:
        row.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"subscription_list:{page - 1}"
            )
        )

    if page < total_pages:
        row.append(
            InlineKeyboardButton(
                text="➡️ Keyingi",
                callback_data=f"subscription_list:{page + 1}"
            )
        )

    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def subscription_actions_keyboard(subscription_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🗑 O‘chirish",
        callback_data=f"delete_subscription:{subscription_id}"
    )

    builder.adjust(1)
    return builder.as_markup()