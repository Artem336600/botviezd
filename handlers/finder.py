"""Finder flow — FSM for registering a found item."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PhotoSize
from aiogram.fsm.context import FSMContext
from states.forms import FinderForm
from keyboards.builders import (
    categories_keyboard, locations_keyboard, skip_photo_keyboard,
    confirm_keyboard, main_menu_keyboard, admin_item_keyboard
)
from services.api_client import api
from config import ADMIN_CHAT_ID

router = Router()


@router.message(F.text == "🔍 Нашел вещь")
async def finder_start(message: Message, state: FSMContext):
    await state.clear()
    categories = await api.get_categories()
    if not categories:
        await message.answer("⚠️ Не удалось загрузить категории. Попробуй позже.")
        return
    await state.update_data(categories=categories)
    await message.answer(
        "🔍 <b>Регистрация находки</b>\n\nШаг 1/6: Выбери категорию вещи:",
        parse_mode="HTML",
        reply_markup=categories_keyboard(categories),
    )
    await state.set_state(FinderForm.category)


@router.callback_query(FinderForm.category, F.data.startswith("cat:"))
async def finder_category(callback: CallbackQuery, state: FSMContext):
    _, cat_id, cat_name = callback.data.split(":", 2)
    await state.update_data(category_id=int(cat_id), category_name=cat_name)
    await callback.message.edit_text(
        f"✅ Категория: <b>{cat_name}</b>\n\nШаг 2/6: Напиши точное <b>название</b> вещи:",
        parse_mode="HTML",
    )
    await state.set_state(FinderForm.name)


@router.message(FinderForm.name)
async def finder_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer(
        "📸 Шаг 3/6: Прикрепи <b>фото</b> вещи (или пропусти):",
        parse_mode="HTML",
        reply_markup=skip_photo_keyboard(),
    )
    await state.set_state(FinderForm.photo)


@router.message(FinderForm.photo, F.photo)
async def finder_photo(message: Message, state: FSMContext):
    # Save largest photo file_id
    photo: PhotoSize = message.photo[-1]
    await state.update_data(photo_url=None, photo_file_id=photo.file_id)
    await message.answer(
        "🔎 Шаг 4/6: Опиши <b>особые приметы</b> вещи (цвет, царапины, надписи...):",
        parse_mode="HTML",
    )
    await state.set_state(FinderForm.signs)


@router.callback_query(FinderForm.photo, F.data == "skip_photo")
async def finder_skip_photo(callback: CallbackQuery, state: FSMContext):
    await state.update_data(photo_url=None, photo_file_id=None)
    await callback.message.edit_text(
        "🔎 Шаг 4/6: Опиши <b>особые приметы</b> вещи (цвет, царапины, надписи...):",
        parse_mode="HTML",
    )
    await state.set_state(FinderForm.signs)


@router.message(FinderForm.signs)
async def finder_signs(message: Message, state: FSMContext):
    await state.update_data(signs=message.text.strip())
    await message.answer("📍 Шаг 5/6: Где именно ты <b>нашел</b> эту вещь? (опиши место)")
    await state.set_state(FinderForm.where_found)


@router.message(FinderForm.where_found)
async def finder_where(message: Message, state: FSMContext):
    await state.update_data(where_found=message.text.strip())
    locations = await api.get_locations()
    if not locations:
        await message.answer("⚠️ Не удалось загрузить пункты сдачи. Попробуй позже.")
        return
    await state.update_data(locations=locations)
    await message.answer(
        "🏢 Шаг 6/6: Куда ты <b>сдал</b> вещь?",
        reply_markup=locations_keyboard(locations),
    )
    await state.set_state(FinderForm.location)


@router.callback_query(FinderForm.location, F.data.startswith("loc:"))
async def finder_location(callback: CallbackQuery, state: FSMContext):
    _, loc_id, loc_name = callback.data.split(":", 2)
    await state.update_data(location_id=int(loc_id), location_name=loc_name)

    data = await state.get_data()
    summary = (
        f"📋 <b>Проверь данные:</b>\n\n"
        f"📦 Категория: {data['category_name']}\n"
        f"🏷 Название: {data['name']}\n"
        f"🔎 Приметы: {data['signs']}\n"
        f"📍 Где нашел: {data['where_found']}\n"
        f"🏢 Куда сдал: {data['location_name']}\n"
        f"📸 Фото: {'Да' if data.get('photo_file_id') else 'Нет'}"
    )
    await callback.message.edit_text(summary, parse_mode="HTML", reply_markup=confirm_keyboard())
    await state.set_state(FinderForm.confirm)


@router.callback_query(FinderForm.confirm, F.data == "confirm_yes")
async def finder_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user

    item_data = {
        "category_id": data["category_id"],
        "location_id": data["location_id"],
        "name": data["name"],
        "signs": data["signs"],
        "where_found": data["where_found"],
        "photo_url": None,
    }

    result = await api.create_item(
        telegram_id=user.id,
        username=user.username or "",
        first_name=user.first_name or "",
        item_data=item_data,
    )

    if result:
        await callback.message.edit_text(
            "✅ <b>Находка зарегистрирована!</b>\n\n"
            "Она отправлена на модерацию. Администратор проверит и опубликует карточку.\n"
            "Спасибо, что помогаешь людям! 🙏",
            parse_mode="HTML",
        )
        # Notify admin
        if ADMIN_CHAT_ID:
            try:
                await callback.bot.send_message(
                    ADMIN_CHAT_ID,
                    f"🆕 <b>Новая находка #{result['id']}</b>\n\n"
                    f"📦 {data['category_name']}: <b>{data['name']}</b>\n"
                    f"📍 {data['where_found']} → {data['location_name']}\n"
                    f"🔎 Приметы: <i>(скрыты)</i>\n"
                    f"👤 Finder: @{user.username or user.id}",
                    parse_mode="HTML",
                    reply_markup=admin_item_keyboard(result["id"]),
                )
            except Exception:
                pass  # Admin chat not configured
    else:
        await callback.message.edit_text(
            "❌ Произошла ошибка при регистрации. Попробуй снова — /start",
        )
    await state.clear()


@router.callback_query(FinderForm.confirm, F.data == "confirm_no")
async def finder_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Регистрация отменена.")
    await callback.message.answer("Главное меню:", reply_markup=main_menu_keyboard())
