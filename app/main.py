from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.core.config import BOT_TOKEN
from app.database.db import init_db

from app.handlers.start import router as start_router
from app.handlers.admin.subscriptions_menu import router as admin_subscriptions_router
from app.handlers.admin.public_channel import router as public_channel_router
from app.handlers.admin.private_channel import router as private_channel_router
from app.handlers.admin.subscription_list import router as subscription_list_router
from app.handlers.user.subscription_check import router as user_subscription_check_router
from app.middlewares.subscription_middleware import SubscriptionMiddleware
from app.handlers.admin.public_group import router as public_group_router
from app.handlers.admin.private_group import router as private_group_router
from app.handlers.admin.subscription_delete import router as subscription_delete_router
from app.handlers.admin.links import router as links_router

async def start_bot():
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher()

    dp.message.outer_middleware(SubscriptionMiddleware())
    dp.callback_query.outer_middleware(SubscriptionMiddleware())

    dp.include_router(start_router)
    dp.include_router(admin_subscriptions_router)
    dp.include_router(public_channel_router)
    dp.include_router(private_channel_router)
    dp.include_router(subscription_list_router)
    dp.include_router(user_subscription_check_router)
    dp.include_router(public_group_router)
    dp.include_router(private_group_router)
    dp.include_router(links_router)
    dp.include_router(subscription_delete_router)

    print("Bot ishga tushdi 🚀")
    await dp.start_polling(bot)