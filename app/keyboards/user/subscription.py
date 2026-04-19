from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def subscription_check_keyboard(subscriptions, extra_links=None):
    buttons = []

    for index, sub in enumerate(subscriptions, start=1):
        subscription_type = sub.get("subscription_type")

        if subscription_type in ("public_channel", "public_group"):
            username = sub.get("chat_username")
            if not username:
                continue
            username = username.lstrip("@")
            url = f"https://t.me/{username}"

        elif subscription_type in ("private_channel", "private_group"):
            url = sub.get("invite_link")
            if not url:
                continue
        else:
            continue

        buttons.append([
            InlineKeyboardButton(
                text=str(index),
                url=url,
            )
        ])

    if extra_links:
        start_index = len(buttons) + 1
        for idx, sub in enumerate(extra_links, start=start_index):
            url = sub.get("invite_link")
            if not url:
                continue
            buttons.append([
                InlineKeyboardButton(
                    text=str(idx),
                    url=url,
                )
            ])

    buttons.append([
        InlineKeyboardButton(
            text="✅ Tekshirish",
            callback_data="check_subscriptions",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
