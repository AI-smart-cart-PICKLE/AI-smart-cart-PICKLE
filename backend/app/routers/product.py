from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product
from app.schemas import ProductResponse

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

@router.get("/")
def read_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "price": p.price,
            "stock_quantity": p.stock_quantity,
            "image_url": p.image_url,
            "product_info": p.product_info,
        }
        for p in products
    ]

