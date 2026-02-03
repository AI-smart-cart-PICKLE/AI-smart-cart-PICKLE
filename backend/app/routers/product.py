from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional

from app.database import get_db
from app.models import Product, ProductCategory
from app.schemas import ProductResponse, ProductLocationResponse

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

# 상품 목록 조회
@router.get("/", response_model=List[ProductResponse])
def read_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

# 상품 검색 (웹 / pg_trgm 기반) 
@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: str = Query(..., min_length=1, description="검색어"),
    db: Session = Depends(get_db),
):
    """
    상품명으로 상품을 검색합니다. pg_trgm을 활용한 오타 허용(Fuzzy) 검색이 적용됩니다.
    """
    products = (
        db.query(Product)
        .filter(func.similarity(Product.name, q) > 0.2)
        .order_by(func.similarity(Product.name, q).desc())
        .limit(20)
        .all()
    )
    return products

# 상품 상세 조회
@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    상품 상세 정보를 조회합니다.
    """
    product = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.product_id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 조인된 카테고리 정보가 있으면 추가 필드 설정 (ProductResponse 스키마 대응)
    if product.category:
        setattr(product, 'zone_code', product.category.zone_code)
        setattr(product, 'category_name', product.category.name)
        
    return product

# 상품 위치 안내
@router.get("/{product_id}/location", response_model=ProductLocationResponse)
def get_product_location(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.product_id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    category = product.category
    zone_code = category.zone_code if category else "Unknown"

    return ProductLocationResponse(
        product_id=product.product_id,
        name=product.name,
        zone_code=zone_code,
        # TODO: 실제 맵 이미지 URL 로직 필요 시 추가
        map_image_url=f"https://example.com/maps/{zone_code}.png" if zone_code else None
    )

# 바코드로 상품 조회
@router.get("/barcode/{barcode}", response_model=ProductResponse)
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

    return product

