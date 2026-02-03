from .auth import router as auth_router
from .cart import router as cart_router
from .ledger import router as ledger_router
from .payment import router as payment_router
from .product import router as product_router
from .recommendation import router as recommendation_router
from .user import user_router, auth_router as user_auth_router
from .recipe import router as recipe_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "cart_router",
    "ledger_router",
    "payment_router",
    "product_router",
    "recommendation_router",
    "user_router",
    "user_auth_router",
    "recipe_router",
    "admin_router",
]
