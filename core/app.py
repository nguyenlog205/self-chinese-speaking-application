from fastapi import FastAPI
from services.zh_dictionary.src import router as dictionary_router

app = FastAPI(title="Chinese Speaking Application")
app.include_router(dictionary_router, prefix="/vocabulary", tags=["Dictionary"])

@app.get("/")
async def root():
    return {"message": "Chinese Speaking Application API"}