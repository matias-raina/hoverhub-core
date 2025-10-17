from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.auth import AuthRouter
from src.api.routes.users import UserRouter
from src.api.routes.jobs import JobRouter
from src.api.routes.applications import ApplicationRouter
from src.api.routes.favorites import FavoriteRouter
from src.config.database import engine
from src.models import user, job, application, favorite

# Create the FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(AuthRouter().router, prefix="/auth", tags=["auth"])
app.include_router(UserRouter().router, prefix="/users", tags=["users"])
app.include_router(JobRouter().router, prefix="/jobs", tags=["jobs"])
app.include_router(ApplicationRouter().router,
                   prefix="/applications", tags=["applications"])
app.include_router(FavoriteRouter().router,
                   prefix="/favorites", tags=["favorites"])

# Create the database tables


@app.on_event("startup")
def startup_event():
    user.Base.metadata.create_all(bind=engine)
    job.Base.metadata.create_all(bind=engine)
    application.Base.metadata.create_all(bind=engine)
    favorite.Base.metadata.create_all(bind=engine)


# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
