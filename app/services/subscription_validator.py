import re


def validate_title(title: str) -> str | None:
    title = (title or "").strip()

    if not title:
        return "❗ Nomi bo'sh bo'lmasin."

    if len(title) > 100:
        return "❗ Nomi juda uzun. Maksimal 100 ta belgi."

    if not re.search(r"\w", title, re.UNICODE):
        return "❗ Nomi noto'g'ri."

    return None


def parse_username_or_link(value: str) -> tuple[str | None, str | None]:
    value = (value or "").strip()

    username = None
    invite_link = None

    if value.startswith("@"):
        username = value
        invite_link = f"https://t.me/{value[1:]}"
        return username, invite_link

    if value.startswith("https://t.me/") or value.startswith("http://t.me/"):
        invite_link = value
        cleaned = (
            value.replace("https://t.me/", "")
            .replace("http://t.me/", "")
            .strip("/")
        )

        if cleaned and not cleaned.startswith("+") and "joinchat" not in cleaned:
            username = f"@{cleaned}"

        return username, invite_link

    return None, None


def validate_public_channel_data(
    title: str,
    username: str | None,
    invite_link: str | None,
) -> str | None:
    title_error = validate_title(title)
    if title_error:
        return title_error

    if not username:
        return "❗ Ommaviy kanal uchun username aniqlanishi kerak."

    if not username.startswith("@"):
        return "❗ Username noto'g'ri formatda."

    if not invite_link:
        return "❗ Havola aniqlanmadi."

    return None

def validate_private_invite_link(invite_link: str) -> str | None:
    invite_link = (invite_link or "").strip()

    if not invite_link:
        return "❗ Havola bo'sh bo'lmasin."

    if not (
        invite_link.startswith("https://t.me/+")
        or "joinchat" in invite_link
    ):
        return "❗ Maxfiy kanal uchun to‘g‘ri invite link yuboring."

    return None

def is_valid_external_url(url: str) -> bool:
    if not url:
        return False

    url = url.strip()

    return url.startswith("http://") or url.startswith("https://")