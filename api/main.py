from fastapi import FastAPI
from dotenv import load_dotenv
from api.controllers import journal_router
import logging
import os

load_dotenv()

# TODO: Setup basic console logging
# Hint: Use logging.basicConfig() with level=logging.INFO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = FastAPI()
app.include_router(journal_router)