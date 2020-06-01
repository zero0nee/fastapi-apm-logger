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
from elasticapm.handlers.logging import LoggingFilter, Formatter
import elasticapm
from structlog import PrintLogger, wrap_logger
from elasticapm.handlers.structlog import structlog_processor
from structlog.processors import JSONRenderer

# Load dotenv
python_env = os.getenv('PYTHON_ENV') or 'development'
dotenv_path = os.path.join(
    os.path.dirname(__file__),
    '.env.' + python_env
)
dotenv.load_dotenv(dotenv_path)

# Parse loggs to be correlated with APM - https://www.elastic.co/guide/en/apm/agent/python/master/log-correlation.html
# Using structlog https://www.structlog.org/en/stable/examples.html
logger = wrap_logger(PrintLogger(), processors=[structlog_processor,JSONRenderer(indent=1, sort_keys=True)])
log = logger.new()
log.msg("some_event")

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
    log.debug('This is a debug message')
    log.info('This is an info message')
    log.warning('This is a warning message')
    log.error('This is an error message')
    log.critical('This is a critical message')
    log.exception("This is an exception")
    
    # add extra field to logstash message
    extra = {
        'test_string': 'python version: ' + repr(sys.version_info),
        'test_boolean': True,
        'test_dict': {'a': 1, 'b': 'c'},
        'test_float': 1.23,
        'test_integer': 123,
        'test_list': [1, 2, '3'],
    }
    log.info('test extra fields', extra=extra)

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
    log.info('Current transaction_id: ' + str(transaction_id))

    # Get the trace_id of the current transaction’s trace.
    trace_id = elasticapm.get_trace_id()
    log.info('Current trace_id: ' + str(trace_id))

    # Get the id of the current span.
    span_id = elasticapm.get_span_id()
    log.info('Current span_id: ' + str(span_id))

    # As you can also see the apm_client is also accessable from the elasticapm
    elasticapm.Client.logger.root.handlers[0].records == apm_client.logger.root.handlers[0].records
    
    return result

