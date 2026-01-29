from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

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

# 상품 검색 (웹 / pg_trgm 기반) 
@router.get("/search")
def search_products(
    q: str = Query(..., min_length=1, description="검색어"),
    db: Session = Depends(get_db),
):
    products = (
        db.query(Product)
        .filter(func.similarity(Product.name, q) > 0.2)
        .order_by(func.similarity(Product.name, q).desc())
        .limit(20)
        .all()
    )

    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "price": p.price,
            "stock_quantity": p.stock_quantity,
            "in_stock": p.stock_quantity > 0,
            "image_url": p.image_url,
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

