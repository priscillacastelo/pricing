from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
import math

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StickerMaterial(str, Enum):
    vinyl = "vinyl"
    holographic = "holographic"


class StickerRequest(BaseModel):
    width: float
    height: float
    quantity: int
    material: StickerMaterial


COST_PER_CM2 = 0.002299857628
BASE_COST = 0.05
PROFIT_MARGIN_PER_CM2 = 0.005
HOLOGRAPHIC_MARKUP = 1.1


def calculate_unit_price(width: float, height: float, material: StickerMaterial) -> float:
    area = width * height
    size_factor = area * (COST_PER_CM2 + PROFIT_MARGIN_PER_CM2)
    unit_price = BASE_COST + size_factor

    if material == StickerMaterial.holographic:
        unit_price *= HOLOGRAPHIC_MARKUP

    return unit_price


def calculate_quantity_factor(quantity: int) -> float:
    return 0.98 - (math.log(quantity) / 100)


@app.post("/calculate-price")
async def calculate_price(sticker: StickerRequest):
    unit_price = calculate_unit_price(sticker.width, sticker.height, sticker.material)
    quantity_factor = calculate_quantity_factor(sticker.quantity)

    discounted_unit_price = unit_price * quantity_factor
    total_price = discounted_unit_price * sticker.quantity

    bulk_discount = 0
    discount_explanation = None

    if sticker.quantity >= 500:
        bulk_discount = total_price * 0.05
        total_price -= bulk_discount
        discount_explanation = "5% bulk discount applied for ordering 500 or more stickers"

    return {
        "base_unit_price": round(unit_price, 2),
        "discounted_unit_price": round(discounted_unit_price, 2),
        "total_price": round(total_price, 2),
        "bulk_discount": round(bulk_discount, 2),
        "discount_explanation": discount_explanation
    }