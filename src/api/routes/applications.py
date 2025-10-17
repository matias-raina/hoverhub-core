from fastapi import APIRouter, Depends, HTTPException
from src.schemas.application import ApplicationCreate, ApplicationResponse
from src.services.application_service import ApplicationService
from src.api.dependencies import get_current_user


class ApplicationRouter:
    def __init__(self):
        self.router = APIRouter()
        self.application_service = ApplicationService()

        self.router.add_api_route(
            "/", self.submit_application, methods=["POST"], response_model=ApplicationResponse)
        self.router.add_api_route(
            "/", self.get_applications, methods=["GET"], response_model=list[ApplicationResponse])

    async def submit_application(self, application: ApplicationCreate, current_user: str = Depends(get_current_user)):
        try:
            return await self.application_service.submit_application(application, current_user)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_applications(self, current_user: str = Depends(get_current_user)):
        try:
            return await self.application_service.get_applications(current_user)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


application_router = ApplicationRouter().router
