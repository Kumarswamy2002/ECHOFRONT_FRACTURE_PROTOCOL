from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List
from backend.app.models.entities import Profile, Item, Inventory, Transaction, Purchase
from backend.app.schemas.game_schemas import StoreItemResponse, PurchaseItemRequest

class EconomyService:
    @staticmethod
    async def get_store_catalog(db: AsyncSession) -> List[StoreItemResponse]:
        res = await db.execute(select(Item).where(Item.is_available_in_store == True))
        items = res.scalars().all()
        return [
            StoreItemResponse(
                id=item.id,
                item_code=item.item_code,
                name=item.name,
                description=item.description,
                item_type=item.item_type,
                rarity=item.rarity,
                price_credits=item.price_credits,
                price_shards=item.price_shards,
                asset_reference=item.asset_reference
            )
            for item in items
        ]

    @staticmethod
    async def process_purchase(db: AsyncSession, profile_id: str, req: PurchaseItemRequest) -> dict:
        # Check idempotency
        idempotent_check = await db.execute(select(Purchase).where(Purchase.idempotency_key == req.idempotency_key))
        if idempotent_check.scalar_one_or_none():
            return {"status": "success", "message": "Transaction previously processed."}

        # Fetch item
        item_res = await db.execute(select(Item).where(Item.id == req.item_id))
        item = item_res.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store item not found.")

        # Fetch profile
        prof_res = await db.execute(select(Profile).where(Profile.id == profile_id))
        profile = prof_res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")

        price = item.price_credits if req.currency_type == "credits" else item.price_shards
        if req.currency_type == "credits":
            if profile.credits < price:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient credits.")
            profile.credits -= price
            balance_after = profile.credits
        else:
            if profile.fracture_shards < price:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient fracture shards.")
            profile.fracture_shards -= price
            balance_after = profile.fracture_shards

        # 1. Record Ledger Transaction
        tx = Transaction(
            profile_id=profile.id,
            currency_type=req.currency_type,
            amount=-price,
            balance_after=balance_after,
            transaction_reason=f"store_purchase_{item.item_code}",
            reference_id=item.id
        )
        db.add(tx)

        # 2. Record Purchase
        purchase = Purchase(
            profile_id=profile.id,
            item_id=item.id,
            currency_type=req.currency_type,
            price_paid=price,
            idempotency_key=req.idempotency_key
        )
        db.add(purchase)

        # 3. Grant Item to Inventory
        inv_res = await db.execute(select(Inventory).where(
            (Inventory.profile_id == profile.id) & (Inventory.item_id == item.id)
        ))
        inv_item = inv_res.scalar_one_or_none()
        if inv_item:
            inv_item.quantity += 1
        else:
            new_inv = Inventory(
                profile_id=profile.id,
                item_id=item.id,
                quantity=1
            )
            db.add(new_inv)

        await db.commit()
        return {
            "status": "success",
            "item_name": item.name,
            "currency_used": req.currency_type,
            "price_paid": price,
            "remaining_balance": balance_after
        }
