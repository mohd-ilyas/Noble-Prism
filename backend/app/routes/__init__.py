from app.routes.agents import router as agents_router
from app.routes.policies import router as policies_router
from app.routes.transactions import router as transactions_router
from app.routes.ledger import router as ledger_router
from app.routes.insights import router as insights_router
from app.routes.killswitch import router as killswitch_router
from app.routes.commerce import router as commerce_router

__all__ = [
    "agents_router",
    "policies_router",
    "transactions_router",
    "ledger_router",
    "insights_router",
    "killswitch_router",
    "commerce_router",
]
