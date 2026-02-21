"""Loser flow — FSM for registering a lost item search."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PhotoSize
from aiogram.fsm.context import FSMContext
from states.forms import LoserForm
from keyboards.builders import skip_photo_keyboard, confirm_keyboard, main_menu_keyboard, miniapp_keyboard
from services.api_client import api
from config import MINIAPP_URL

router = Router()


@router.message(F.text == "😔 Потерял вещь")
async def loser_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "😔 <b>Заявка на поиск вещи</b>\n\n"
        "Сначала загляни в Mini App — возможно, твоя вещь уже найдена!\n\n"
        "Если не нашёл — заполни заявку, и мы сообщим тебе, как только появится совпадение.\n\n"
        "Шаг 1/3: Напиши <b>название</b> потерянной вещи:",
        parse_mode="HTML",
        reply_markup=miniapp_keyboard(MINIAPP_URL, "📱 Проверить находки"),
    )
    await state.set_state(LoserForm.name)


@router.message(LoserForm.name)
async def loser_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer(
        "🔎 Шаг 2/3: Опиши <b>особые признаки</b> своей вещи\n"
        "(цвет, царапины, надписи, чехол, брелок и т.д.):",
        parse_mode="HTML",
    )
    await state.set_state(LoserForm.signs)


@router.message(LoserForm.signs)
async def loser_signs(message: Message, state: FSMContext):
    await state.update_data(signs=message.text.strip())
    await message.answer(
        "📸 Шаг 3/3: Прикрепи <b>фото</b> вещи (опционально):",
        parse_mode="HTML",
        reply_markup=skip_photo_keyboard(),
    )
    await state.set_state(LoserForm.photo)


@router.message(LoserForm.photo, F.photo)
async def loser_photo(message: Message, state: FSMContext):
    photo: PhotoSize = message.photo[-1]
    await state.update_data(photo_file_id=photo.file_id)
    await _loser_show_confirm(message, state)


@router.callback_query(LoserForm.photo, F.data == "skip_photo")
async def loser_skip_photo(callback: CallbackQuery, state: FSMContext):
    await state.update_data(photo_file_id=None)
    await callback.message.delete()
    await _loser_show_confirm(callback.message, state)


async def _loser_show_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    summary = (
        f"📋 <b>Проверь заявку:</b>\n\n"
        f"🏷 Вещь: {data['name']}\n"
        f"🔎 Признаки: {data['signs']}\n"
        f"📸 Фото: {'Да' if data.get('photo_file_id') else 'Нет'}"
    )
    await message.answer(summary, parse_mode="HTML", reply_markup=confirm_keyboard())
    await state.set_state(LoserForm.confirm)


@router.callback_query(LoserForm.confirm, F.data == "confirm_yes")
async def loser_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user

    result = await api.create_lost_request(
        telegram_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        data={"name": data["name"], "signs": data["signs"], "photo_url": None},
    )

    if result:
        await callback.message.edit_text(
            "✅ <b>Заявка принята!</b>\n\n"
            "Администратор просмотрит её и, если найдут совпадение с поступившей находкой, "
            "свяжется с тобой в этом чате.\n\n"
            "📋 Статус заявки можно посмотреть через «<b>Мои заявки</b>».",
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text("❌ Ошибка при отправке заявки. Попробуй снова — /start")

    await state.clear()


@router.callback_query(LoserForm.confirm, F.data == "confirm_no")
async def loser_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Заявка отменена.")
    await callback.message.answer("Главное меню:", reply_markup=main_menu_keyboard())


# ─── My Claims ───────────────────────────────────────────────────────────────

@router.message(F.text == "📋 Мои заявки")
async def my_claims(message: Message):
    claims = await api.get_my_claims(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
    )
    if not claims:
        await message.answer("У тебя пока нет заявок на возврат вещей.")
        return

    STATUS_ICONS = {
        "pending": "⏳ На рассмотрении",
        "approved": "✅ Одобрено",
        "rejected": "❌ Отклонено",
        "appeal_pending": "📤 Апелляция на рассмотрении",
    }
    lines = []
    for c in claims[:10]:
        status = STATUS_ICONS.get(c["status"], c["status"])
        lines.append(f"#{c['id']} — {status}")
        if c.get("admin_comment"):
            lines.append(f"   💬 {c['admin_comment']}")

    await message.answer(
        "📋 <b>Твои заявки:</b>\n\n" + "\n".join(lines),
        parse_mode="HTML",
    )
