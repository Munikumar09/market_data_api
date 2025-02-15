# pylint: disable=missing-function-docstring

from pathlib import Path

import redis.asyncio as redis
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from app.data_layer.database.db_connections import postgresql
from app.routers.authentication import authentication
from app.routers.nse.derivatives import derivatives
from app.routers.nse.equity import equity
from app.routers.smartapi.smartapi import smartapi
from app.utils.common.logger import get_logger
from app.utils.fetch_data import get_required_env_var
from app.utils.startup_utils import create_smartapi_tokens_db

logger = get_logger(Path(__file__).name)

load_dotenv()

app = FastAPI()


# Initialize Redis client
REDIS_HOST = get_required_env_var("REDIS_HOST")
REDIS_PORT = int(get_required_env_var("REDIS_PORT"))
REDIS_DB = get_required_env_var("REDIS_DB")
try:
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
    )

except redis.ConnectionError as e:
    logger.error("Failed to connect to Redis: %s", str(e))
    raise


@app.on_event("startup")
async def startup_event():
    try:
        postgresql.create_db_and_tables()
        create_smartapi_tokens_db()
        await redis_client
        await FastAPILimiter.init(redis_client)
    except Exception as e:
        logger.error("Failed to initialize startup event: %s", str(e))
        raise


app.include_router(derivatives.router)
app.include_router(equity.router)
app.include_router(smartapi.router)
app.include_router(authentication.router)


@app.get("/", response_model=str)
def index():
    return "This is main page"


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
