"""HTTP API client for bot → backend communication."""
import aiohttp
import logging
from typing import Optional
from config import API_BASE_URL

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def _get_token(self, telegram_id: int, username: str = "", first_name: str = "") -> Optional[str]:
        """Get JWT for given telegram_id (dev mode — no initData)."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/auth/telegram",
                json={"telegram_id": telegram_id, "username": username, "first_name": first_name},
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("access_token")
                logger.error("Auth failed: %s %s", resp.status, await resp.text())
                return None

    async def get_categories(self) -> list:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{self.base_url}/categories") as r:
                return await r.json() if r.status == 200 else []

    async def get_locations(self) -> list:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{self.base_url}/locations") as r:
                return await r.json() if r.status == 200 else []

    async def create_item(self, telegram_id: int, username: str, first_name: str, item_data: dict) -> Optional[dict]:
        token = await self._get_token(telegram_id, username, first_name)
        if not token:
            return None
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{self.base_url}/items",
                json=item_data,
                headers={"Authorization": f"Bearer {token}"},
            ) as r:
                if r.status == 201:
                    return await r.json()
                logger.error("create_item failed: %s %s", r.status, await r.text())
                return None

    async def create_lost_request(
        self, telegram_id: int, username: str, first_name: str, data: dict
    ) -> Optional[dict]:
        token = await self._get_token(telegram_id, username, first_name)
        if not token:
            return None
        async with aiohttp.ClientSession() as s:
            async with s.post(
                f"{self.base_url}/lost-requests",
                json=data,
                headers={"Authorization": f"Bearer {token}"},
            ) as r:
                if r.status == 201:
                    return await r.json()
                logger.error("create_lost_request failed: %s %s", r.status, await r.text())
                return None

    async def get_my_claims(self, telegram_id: int, username: str, first_name: str) -> list:
        token = await self._get_token(telegram_id, username, first_name)
        if not token:
            return []
        async with aiohttp.ClientSession() as s:
            async with s.get(
                f"{self.base_url}/claims/my",
                headers={"Authorization": f"Bearer {token}"},
            ) as r:
                return await r.json() if r.status == 200 else []

    async def admin_approve_item(self, admin_telegram_id: int, item_id: int) -> bool:
        token = await self._get_token(admin_telegram_id)
        if not token:
            return False
        async with aiohttp.ClientSession() as s:
            async with s.patch(
                f"{self.base_url}/admin/items/{item_id}",
                json={"status": "active"},
                headers={"Authorization": f"Bearer {token}"},
            ) as r:
                return r.status == 200

    async def admin_delete_item(self, admin_telegram_id: int, item_id: int) -> bool:
        token = await self._get_token(admin_telegram_id)
        if not token:
            return False
        async with aiohttp.ClientSession() as s:
            async with s.delete(
                f"{self.base_url}/admin/items/{item_id}",
                headers={"Authorization": f"Bearer {token}"},
            ) as r:
                return r.status == 204

    async def admin_approve_claim(self, admin_telegram_id: int, claim_id: int) -> Optional[dict]:
        token = await self._get_token(admin_telegram_id)
        if not token:
            return None
        async with aiohttp.ClientSession() as s:
            async with s.patch(
                f"{self.base_url}/admin/claims/{claim_id}",
                json={"status": "approved", "admin_comment": "Вещь ваша. Заберите по адресу в сообщении."},
                headers={"Authorization": f"Bearer {token}"},
            ) as r:
                return await r.json() if r.status == 200 else None

    async def admin_reject_claim(self, admin_telegram_id: int, claim_id: int, comment: str = "") -> Optional[dict]:
        token = await self._get_token(admin_telegram_id)
        if not token:
            return None
        async with aiohttp.ClientSession() as s:
            async with s.patch(
                f"{self.base_url}/admin/claims/{claim_id}",
                json={"status": "rejected", "admin_comment": comment or "Заявка не подтверждена"},
                headers={"Authorization": f"Bearer {token}"},
            ) as r:
                return await r.json() if r.status == 200 else None


api = APIClient()
