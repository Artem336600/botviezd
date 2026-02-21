"""Start handler — /start and main menu routing."""
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.builders import main_menu_keyboard, miniapp_keyboard
from config import MINIAPP_URL

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    name = message.from_user.first_name or "друг"
    await message.answer(
        f"👋 Привет, {name}!\n\n"
        "Это бюро находок. Выбери действие:\n\n"
        "🔍 <b>Нашел вещь</b> — зарегистрировать находку\n"
        "😔 <b>Потерял вещь</b> — подать заявку на поиск\n"
        "📋 <b>Мои заявки</b> — статус твоих заявок\n\n"
        "Или открой Mini App, чтобы посмотреть все находки:",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )
    await message.answer(
        "📱 Смотри ленту находок:",
        reply_markup=miniapp_keyboard(MINIAPP_URL),
    )
