import traceback
from fastapi import FastAPI
import logging
from datetime import datetime
from pydantic import BaseModel
from fastapi.responses import RedirectResponse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),   # log to a file
        logging.StreamHandler()           # also log to console
    ]
)

logger = logging.getLogger(__name__)

class MessageRequest(BaseModel):
    message: str

list_of_messages = []

# Create FastAPI app
app = FastAPI()

@app.get("/")
def root():
    """Currently redirecting to swagger page"""
    return RedirectResponse("/docs")


@app.post("/message")
async def ping(request: MessageRequest):
    try:
        list_of_messages.append(request.message)
        print(list_of_messages)
        return request.message
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Something went wrong: {e}")