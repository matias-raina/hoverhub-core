from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.schemas.offer_schema import OfferCreate, OfferUpdate
from src.services.offer_service import OfferService
from src.api.dependencies import get_current_user, get_user_repository

router = APIRouter(prefix="/offers", tags=["Offers"])

@router.post("/")
def create_offer(offer_data: OfferCreate, db: Session = Depends(get_user_repository), user=Depends(get_current_user)):
    service = OfferService(db)
    return service.create_offer(offer_data, user)

@router.get("/")
def get_offers(db: Session = Depends(get_user_repository)):
    service = OfferService(db)
    return service.get_offers()

@router.put("/{offer_id}")
def update_offer(offer_id: int, data: OfferUpdate, db: Session = Depends(get_user_repository), user=Depends(get_current_user)):
    service = OfferService(db)
    return service.update_offer(offer_id, data, user)
