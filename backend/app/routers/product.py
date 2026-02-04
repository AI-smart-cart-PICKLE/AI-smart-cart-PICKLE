from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.models import Product, ProductCategory

router = APIRouter(
    prefix="/api/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

# 카테고리 목록 조회
@router.get("/categories")
def read_categories(db: Session = Depends(get_db)):
    categories = db.query(ProductCategory).all()
    return [
        {
            "category_id": c.category_id,
            "name": c.name,
            "zone_code": c.zone_code,
        }
        for c in categories
    ]

# 상품 목록 조회
@router.get("/")
def read_products(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    products = query.all()
    
    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "price": p.price,
            "stock_quantity": p.stock_quantity,
            "image_url": p.image_url,
            "product_info": p.product_info,
            "category_name": p.category.name if p.category else None,
            "zone_code": p.category.zone_code if p.category else None,
        }
        for p in products
    ]

# 상품 검색 (웹 / pg_trgm 기반)
@router.get("/search")
def search_products(
    q: str = Query(..., min_length=1, description="검색어"),
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    print(f"DEBUG: Searching for keyword: '{q}' in category: {category_id}")
    
    # 1. 유사도 검색과 LIKE 검색 결합
    # HINT:similarity 함수에 명시적 타입 캐스팅 추가 (character varying)
    similarity_col = func.similarity(Product.name, q)
    search_filter = (Product.name.ilike(f"%{q}%")) | (similarity_col > 0.1)
    
    query = db.query(Product).filter(search_filter)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = (
        query
        .order_by(similarity_col.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "product_id": p.product_id,
            "name": p.name,
            "price": p.price,
            "stock_quantity": p.stock_quantity,
            "in_stock": (p.stock_quantity or 0) > 0,
            "image_url": p.image_url,
            "category_name": p.category.name if p.category else None,
            "zone_code": p.category.zone_code if p.category else None,
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
        "category_name": product.category.name if product.category else None,
        "zone_code": product.category.zone_code if product.category else None,
    }

# 상품 위치 안내
@router.get("/{product_id}/location")
def get_product_location(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .join(ProductCategory)
        .filter(Product.product_id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    category = product.category  # relationship 기준

    return {
        "product_id": product.product_id,
        "category": category.name,
        "zone_code": category.zone_code,
        "aisle": category.zone_code.split("-")[0],  # A / B / C
    }

# 바코드로 상품 조회
@router.get("/barcode/{barcode}")
def get_product_by_barcode(
    barcode: str,
    db: Session = Depends(get_db)
):
    clean_barcode = barcode.strip()

    product = (
        db.query(Product)
        .filter(Product.barcode == clean_barcode)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="상품을 찾을 수 없습니다."
        )

    return {
        "product_id": product.product_id,
        "name": product.name,
        "price": product.price,
        "stock_quantity": product.stock_quantity,
        "image_url": product.image_url,
        "barcode": product.barcode,
    }
