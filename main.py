#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import random
import time
import dotenv
import logging
from fastapi import Body, FastAPI
from pydantic import BaseModel
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from elasticapm.handlers.logging import LoggingFilter
from elasticapm.handlers.logging import Formatter
import elasticapm
import logstash

# Load dotenv
python_env = os.getenv('PYTHON_ENV') or 'development'
dotenv_path = os.path.join(
    os.path.dirname(__file__),
    '.env.' + python_env
)
dotenv.load_dotenv(dotenv_path)

# Define a logstash logger.
host = '127.0.0.1'
port = 5000
logger = logging.getLogger('python-logstash-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logstash.LogstashHandler(host, port, version=1))

# Create the fastapi app
app = FastAPI()

# Creating the fastapi apm middleware
# https://www.elastic.co/guide/en/apm/agent/python/master/starlette-support.html
settings = {
    'SERVER_URL':os.environ.get('APM_SERVER_URL'),
    'SERVICE_NAME':os.environ.get('APM_SEVICE_NAME'),
    'SECRET_TOKEN':os.environ.get('APM_SECRET_TOKEN'),
    'CAPTURE_BODY':'all',
    'CAPTURE_HEADERS': True,
    'DEBUG': True,
    } # Just for demo
apm_client = make_apm_client(settings)
app.add_middleware(ElasticAPM, client=apm_client)


# Below is a fast API example app
# https://fastapi.tiangolo.com/
class Purchase(BaseModel):
    username: str
    email: str = None
    cost_spend: float = None
    item_count: int = None

class Billing(Purchase):
    id: str
    billing_amount: float


@app.post("/checkout", response_model=Billing)
def checkout(request: Purchase = Body(...)):
    """Signup user.
    """
    result = {
        'id': time.time(),
        'username': request.username,
        'email': request.email,
        'cost_spend': request.cost_spend,
        'item_count': request.item_count,
        'billing_amount': request.cost_spend * request.item_count,
    }

    #Different logging levels
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
    logger.exception("This is an exception")
    
    # add extra field to logstash message
    extra = {
        'test_string': 'python version: ' + repr(sys.version_info),
        'test_boolean': True,
        'test_dict': {'a': 1, 'b': 'c'},
        'test_float': 1.23,
        'test_integer': 123,
        'test_list': [1, 2, '3'],
    }
    logger.info('test extra fields', extra=extra)

    #Capture an arbitrary exception by calling capture_exception:
    try:
        1 / 0
    except ZeroDivisionError:
        apm_client.capture_exception()

    # Log a generic message with capture_message:
    apm_client.capture_message('hello, world!')

    # Alternatively, a parameterized message as a dictionary.
    apm_client.capture_message(param_message={
        'message': 'Billing process for %s succeeded. Amount: %s',
        'params': (result['id'], result['billing_amount']),
    })

    # Get the id of the current transaction.
    transaction_id = elasticapm.get_transaction_id()
    logger.info('Current transaction_id: ' + str(transaction_id))

    # Get the trace_id of the current transaction’s trace.
    trace_id = elasticapm.get_trace_id()
    logger.info('Current trace_id: ' + str(trace_id))

    # Get the id of the current span.
    span_id = elasticapm.get_span_id()
    logger.info('Current span_id: ' + str(span_id))

    return result

