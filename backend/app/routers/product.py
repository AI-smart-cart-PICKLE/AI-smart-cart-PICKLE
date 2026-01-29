from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

# 상품 목록 조회
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


# 상품 상세 조회
@router.get("/{product_id}")
def read_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.product_id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return {
        "product_id": product.product_id,
        "name": product.name,
        "price": product.price,
        "stock_quantity": product.stock_quantity,
        "image_url": product.image_url,
        "product_info": product.product_info,
    }
