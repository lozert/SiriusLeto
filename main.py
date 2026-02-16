from fastapi import FastAPI

from app.api.v1.routers import authors, health, organization_topics, recommendations


app = FastAPI(title="SciTinder API")


app.include_router(health.router)
app.include_router(authors.router)
app.include_router(recommendations.router)
app.include_router(organization_topics.router)


@app.get("/")
def root():
    return {"message": "SciTinder API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

