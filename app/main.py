from fastapi import FastAPI
from app.api.routes import users

app = FastAPI(title="My FastAPI app")

# include routers
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Welcome to my FastAPI With SQLALchemy"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
