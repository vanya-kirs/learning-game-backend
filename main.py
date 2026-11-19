from fastapi import FastAPI

from api.v1.web.web_game_router import web_game_router

app = FastAPI(title="Learning Game API")
app.include_router(web_game_router)
