from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📢 Majburiy obunalar"), KeyboardButton(text="🎬 Kinolar bazasi")],
        [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="👥 Foydalanuvchilar")]
    ],
    resize_keyboard=True
)