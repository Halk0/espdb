
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, File, UploadFile
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from db_handler_mysql import database_handler
from dotenv import load_dotenv
from logger import setup_logging
import os
import datetime
import uuid
import json
from models import WiFiscan, ProbeData
import sys

pwd = os.path.dirname(os.path.realpath(__file__))
dotenv_path = os.path.join(pwd, '.env')
load_dotenv(dotenv_path)
app = FastAPI()
db_handle = database_handler()
logger = setup_logging("fastapi")
api_key = os.environ.get('api_key')

# Adds Fastapi the ability to return data to servers who originate from different address/port
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


def validate_user(given_api_key: Optional[str] = Header(None)):
    logger.debug(str(type(api_key)) + str(type(given_api_key)))
    logger.debug(
        f'Comparing these api_keys ORIGINAL: {api_key} GIVEN: {given_api_key}')
    if given_api_key == api_key:
        logger.debug('Authenticated using api key from headers')
        return True
    else:
        raise HTTPException(status_code=403, detail={'success': False})


@app.post('/new/wifiscan/data')
def new_playlist(data: WiFiscan, X_API_KEY: Optional[str] = Header(None)):
    try:
        validate_user(X_API_KEY)
        connection = database_handler()
        wifiscandata = jsonable_encoder(data)
        logger.debug(type(wifiscandata))
        logger.debug(f"this is the received json: {wifiscandata}")
        connection.add_WiFiData(wifiscandata)
        return {"success": True}
    except Exception as e:
        logger.exception(f"Ran in to an exception: {e}")
        return e


@app.post('/new/probe/data')
def new_probedata(data: ProbeData, X_API_KEY: Optional[str] = Header(None)):
    try:
        validate_user(X_API_KEY)
        connection = database_handler()
        probeddata = jsonable_encoder(data)
        logger.debug(type(probeddata))
        logger.debug(f"this is the received json: {probeddata}")
        connection.add_ProbeData(probeddata)
        return {"success": True}
    except Exception as e:
        logger.exception(f"Ran in to an exception: {e}")
        return e
        

@app.get('/wifidata')
def wifi_data(X_API_KEY: Optional[str] = Header(None)):
    validate_user(X_API_KEY)
    connection = database_handler()
    data = connection.get_wifi_data()
    if data == False:
        return {"success": False}
    else:
        return data

@app.get('/probedata')
def probe_data(X_API_KEY: Optional[str] = Header(None)):
    validate_user(X_API_KEY)
    connection = database_handler()
    data = connection.get_probe_data()
    if data == False:
        return {"success": False}
    else:
        return data

@app.get('/')
def read_root():
    return {'test': 'works'}
