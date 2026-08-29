from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List
from backend.app.models.entities import Inventory, Item, Loadout, Profile
from backend.app.schemas.game_schemas import InventoryItemResponse, LoadoutResponse, LoadoutUpdateRequest

class InventoryService:
    @staticmethod
    async def get_player_inventory(db: AsyncSession, profile_id: str) -> List[InventoryItemResponse]:
        query = select(Inventory, Item).join(Item, Inventory.item_id == Item.id).where(Inventory.profile_id == profile_id)
        result = await db.execute(query)
        rows = result.all()

        inventory_list = []
        for inv, item in rows:
            inventory_list.append(InventoryItemResponse(
                inventory_id=inv.id,
                item_id=item.id,
                item_code=item.item_code,
                name=item.name,
                item_type=item.item_type,
                rarity=item.rarity,
                quantity=inv.quantity,
                asset_reference=item.asset_reference,
                acquired_at=inv.acquired_at
            ))
        return inventory_list

    @staticmethod
    async def get_player_loadouts(db: AsyncSession, profile_id: str) -> List[LoadoutResponse]:
        result = await db.execute(select(Loadout).where(Loadout.profile_id == profile_id))
        loadouts = result.scalars().all()
        return [
            LoadoutResponse(
                id=l.id,
                operative_code=l.operative_code,
                loadout_name=l.loadout_name,
                primary_weapon_code=l.primary_weapon_code,
                secondary_weapon_code=l.secondary_weapon_code,
                tactical_gadget=l.tactical_gadget,
                cosmetic_skin_item_id=l.cosmetic_skin_item_id,
                is_active=l.is_active
            )
            for l in loadouts
        ]

    @staticmethod
    async def update_or_create_loadout(db: AsyncSession, profile_id: str, req: LoadoutUpdateRequest) -> LoadoutResponse:
        res = await db.execute(select(Loadout).where(
            (Loadout.profile_id == profile_id) & (Loadout.operative_code == req.operative_code)
        ))
        loadout = res.scalar_one_or_none()

        if not loadout:
            loadout = Loadout(
                profile_id=profile_id,
                operative_code=req.operative_code,
                loadout_name=req.loadout_name or f"{req.operative_code} Default",
                primary_weapon_code=req.primary_weapon_code or "WEAPON_AR_VORTEX",
                secondary_weapon_code=req.secondary_weapon_code or "WEAPON_PISTOL_ION",
                tactical_gadget=req.tactical_gadget or "GADGET_FRAG_GRENADE",
                cosmetic_skin_item_id=req.cosmetic_skin_item_id
            )
            db.add(loadout)
        else:
            if req.loadout_name: loadout.loadout_name = req.loadout_name
            if req.primary_weapon_code: loadout.primary_weapon_code = req.primary_weapon_code
            if req.secondary_weapon_code: loadout.secondary_weapon_code = req.secondary_weapon_code
            if req.tactical_gadget: loadout.tactical_gadget = req.tactical_gadget
            if req.cosmetic_skin_item_id: loadout.cosmetic_skin_item_id = req.cosmetic_skin_item_id

        await db.commit()
        await db.refresh(loadout)

        return LoadoutResponse(
            id=loadout.id,
            operative_code=loadout.operative_code,
            loadout_name=loadout.loadout_name,
            primary_weapon_code=loadout.primary_weapon_code,
            secondary_weapon_code=loadout.secondary_weapon_code,
            tactical_gadget=loadout.tactical_gadget,
            cosmetic_skin_item_id=loadout.cosmetic_skin_item_id,
            is_active=loadout.is_active
        )
