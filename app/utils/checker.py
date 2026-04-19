async def is_user_subscribed(bot, chat_identifier, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(
            chat_id=chat_identifier,
            user_id=user_id
        )
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


async def is_bot_admin_in_chat(bot, chat_identifier) -> bool:
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(
            chat_id=chat_identifier,
            user_id=me.id
        )
        return member.status in ("administrator", "creator")
    except Exception:
        return False