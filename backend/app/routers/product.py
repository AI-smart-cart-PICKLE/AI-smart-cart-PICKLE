from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.db.database import get_db
from app.models import Product, ProductCategory
from app.schemas import ProductResponse, ProductLocationResponse

router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={404: {"description": "Not found"}},
)

@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    q: str = Query(..., description="검색어 (상품명)"),
    category_key: Optional[str] = Query(None, description="카테고리 필터 (예: on_sale, best - 현재 미구현)"),
    db: Session = Depends(get_db)
):
    """
    상품명으로 상품을 검색합니다.
    - 대소문자 구분 없이 검색 (ilike)
    - 카테고리 정보와 위치 정보(zone_code)를 포함하여 반환합니다.
    """
    if not q:
        return []

    # 기본 검색: 이름에 검색어 포함
    query = db.query(Product, ProductCategory).outerjoin(Product.category)
    query = query.filter(Product.name.ilike(f"%{q}%"))
    
    # 결과 조회
    results = query.all()
    
    response = []
    for product, category in results:
        p_dict = product.__dict__
        if category:
            p_dict['zone_code'] = category.zone_code
            p_dict['category_name'] = category.name
        else:
            p_dict['zone_code'] = None
            p_dict['category_name'] = None
            
        response.append(ProductResponse(**p_dict))
        
    return response


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    상품 상세 정보를 조회합니다.
    """
    result = db.query(Product, ProductCategory).outerjoin(Product.category).filter(Product.product_id == product_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
        
    product, category = result
    
    p_dict = product.__dict__
    if category:
        p_dict['zone_code'] = category.zone_code
        p_dict['category_name'] = category.name
    else:
        p_dict['zone_code'] = None
        p_dict['category_name'] = None
        
    return ProductResponse(**p_dict)


@router.get("/{product_id}/location", response_model=ProductLocationResponse)
async def get_product_location(product_id: int, db: Session = Depends(get_db)):
    """
    상품의 위치(Zone) 정보를 조회합니다.
    """
    result = db.query(Product, ProductCategory).outerjoin(Product.category).filter(Product.product_id == product_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
        
    product, category = result
    
    zone_code = category.zone_code if category else "Unknown"
    
    return ProductLocationResponse(
        product_id=product.product_id,
        name=product.name,
        zone_code=zone_code,
        # TODO: 실제 맵 이미지 URL 로직 필요 시 추가
        map_image_url=f"https://example.com/maps/{zone_code}.png" if zone_code else None
    )