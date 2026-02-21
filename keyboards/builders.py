from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🔍 Нашел вещь"),
        KeyboardButton(text="😔 Потерял вещь"),
    )
    builder.row(KeyboardButton(text="📋 Мои заявки"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"cat:{cat['id']}:{cat['name']}",
        )
    builder.adjust(2)
    return builder.as_markup()


def locations_keyboard(locations: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for loc in locations:
        builder.button(
            text=f"📍 {loc['name']}",
            callback_data=f"loc:{loc['id']}:{loc['name'][:20]}",
        )
    builder.adjust(1)
    return builder.as_markup()


def skip_photo_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Пропустить фото", callback_data="skip_photo")
    return builder.as_markup()


def confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Отправить", callback_data="confirm_yes")
    builder.button(text="❌ Отмена", callback_data="confirm_no")
    builder.adjust(2)
    return builder.as_markup()


def admin_item_keyboard(item_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Одобрить", callback_data=f"admin_approve:{item_id}")
    builder.button(text="🗑 Удалить", callback_data=f"admin_delete:{item_id}")
    builder.adjust(2)
    return builder.as_markup()


def admin_claim_keyboard(claim_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Принять", callback_data=f"claim_approve:{claim_id}")
    builder.button(text="❌ Отклонить", callback_data=f"claim_reject:{claim_id}")
    builder.adjust(2)
    return builder.as_markup()


def miniapp_keyboard(url: str, text: str = "📱 Открыть Mini App") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text, web_app={"url": url})
    return builder.as_markup()
