"""Admin callbacks — item approval/deletion, claim moderation from bot notifications."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from services.api_client import api

router = Router()


@router.callback_query(F.data.startswith("admin_approve:"))
async def admin_approve_item(callback: CallbackQuery):
    item_id = int(callback.data.split(":")[1])
    admin_tg_id = callback.from_user.id

    ok = await api.admin_approve_item(admin_tg_id, item_id)
    if ok:
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ <b>Одобрено и опубликовано!</b>",
            parse_mode="HTML",
        )
        await callback.answer("✅ Находка одобрена")
    else:
        await callback.answer("❌ Ошибка — проверь права администратора", show_alert=True)


@router.callback_query(F.data.startswith("admin_delete:"))
async def admin_delete_item(callback: CallbackQuery):
    item_id = int(callback.data.split(":")[1])
    admin_tg_id = callback.from_user.id

    ok = await api.admin_delete_item(admin_tg_id, item_id)
    if ok:
        await callback.message.edit_text(
            callback.message.text + "\n\n🗑 <b>Удалено</b>",
            parse_mode="HTML",
        )
        await callback.answer("🗑 Находка удалена")
    else:
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("claim_approve:"))
async def admin_approve_claim(callback: CallbackQuery):
    claim_id = int(callback.data.split(":")[1])
    admin_tg_id = callback.from_user.id

    result = await api.admin_approve_claim(admin_tg_id, claim_id)
    if result:
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ <b>Заявка одобрена. Уведомление отправлено.</b>",
            parse_mode="HTML",
        )
        await callback.answer("✅ Заявка принята")
    else:
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("claim_reject:"))
async def admin_reject_claim(callback: CallbackQuery):
    claim_id = int(callback.data.split(":")[1])
    admin_tg_id = callback.from_user.id

    result = await api.admin_reject_claim(admin_tg_id, claim_id, "Описание не совпадает с реальной вещью.")
    if result:
        await callback.message.edit_text(
            callback.message.text + "\n\n❌ <b>Заявка отклонена.</b>",
            parse_mode="HTML",
        )
        await callback.answer("❌ Заявка отклонена")
    else:
        await callback.answer("❌ Ошибка", show_alert=True)
