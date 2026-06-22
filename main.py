from fastapi import FastAPI
from database import engine, Base
from routers import events, registrations

# create the tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event Registration API",
    description="A simple API to create events and manage registrations with seat limits and race condition protection",
    version="1.0.0"
)

app.include_router(events.router)
app.include_router(registrations.router)

@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint.
    Confirms the API is running
    """
    return {
        "message": "Event Registration System API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }