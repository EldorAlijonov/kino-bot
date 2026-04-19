from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

subscriptions_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Obuna qo'shish"), KeyboardButton(text="📋 Obunalar ro'yxati")],
        [KeyboardButton(text="✏️ Tahrirlash"), KeyboardButton(text="🗑 O'chirish")],
        [KeyboardButton(text="✅ Aktiv qilish"), KeyboardButton(text="❌ Noaktiv qilish")],
        [KeyboardButton(text="🏠 Admin panel")]
    ],
    resize_keyboard=True
)

add_subscription_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📢 Kanal qo'shish"), KeyboardButton(text="👥 Guruh qo'shish")],
        [KeyboardButton(text="🔗 Havola qo'shish")],
        [KeyboardButton(text="⬅️ Obunalar menyusi"), KeyboardButton(text="🏠 Admin panel")],
    ],
    resize_keyboard=True
)

channel_type_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📢 Ommaviy kanal"), KeyboardButton(text="🔒 Maxfiy kanal")],
        [KeyboardButton(text="⬅️ Qo'shish menyusi"), KeyboardButton(text="🏠 Admin panel")],
    ],
    resize_keyboard=True
)

group_type_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Ommaviy guruh"), KeyboardButton(text="🔒 Maxfiy guruh")],
        [KeyboardButton(text="⬅️ Qo'shish menyusi"), KeyboardButton(text="🏠 Admin panel")],
    ],
    resize_keyboard=True
)

link_type_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔗 Oddiy havola")],
        [KeyboardButton(text="⬅️ Qo'shish menyusi"), KeyboardButton(text="🏠 Admin panel")],
    ],
    resize_keyboard=True
)