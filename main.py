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
from logstash_async.handler import AsynchronousLogstashHandler
import logstash

# Load dotenv
python_env = os.getenv('PYTHON_ENV') or 'development'
dotenv_path = os.path.join(
    os.path.dirname(__file__),
    '.env.' + python_env
)
dotenv.load_dotenv(dotenv_path)

host = '127.0.0.1'
port = 5000

logger = logging.getLogger('python-logstash-logger')
logger.setLevel(logging.INFO)
logger.addHandler(logstash.LogstashHandler(host, port, version=1))

# If you don't want to write to a SQLite database, then you do
# not have to specify a database_path.
# NOTE: Without a database, messages are lost between process restarts.

# Create the fast API app
app = FastAPI()

# Creating middleware
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


# A fast API example 
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
    logger.debug('python-logstash-async: This is a debug message')
    logger.info('python-logstash-async: This is an info message')
    logger.warning('python-logstash-async: This is a warning message')
    logger.error('python-logstash-async: This is an error message')
    logger.critical('python-logstash-async: This is a critical message')
    logger.exception("python-logstash-async: This is an exception")
    
    # add extra field to logstash message
    extra = {
        'test_string': 'python version: ' + repr(sys.version_info),
        'test_boolean': True,
        'test_dict': {'a': 1, 'b': 'c'},
        'test_float': 1.23,
        'test_integer': 123,
        'test_list': [1, 2, '3'],
    }
    logger.info('python-logstash-async: test extra fields', extra=extra)

    #Capture an arbitrary exception by calling capture_exception:
    try:
        1 / 0
    except ZeroDivisionError:
        apm_client.capture_exception()  #WORKS!!!!

    # Log a generic message with capture_message:
    apm_client.capture_message('hello, world!')  #WORKS!!!!

    # Alternatively, a parameterized message as a dictionary.
    apm_client.capture_message(param_message={
        'message': 'Billing process for %s succeeded. Amount: %s',
        'params': (result['id'], result['billing_amount']),
    }) #WORKS!!!!

    # Attach labels to the the current transaction and errors.
    # https://www.elastic.co/guide/en/apm/agent/python/master/api.html#client-api-capture-exception
    #elasticapm.label(ecommerce=True, dollar_value=float(result['cost_spend'])) #TODO DOESNT WORK

    # Attach information about the currently logged in user to the current transaction and errors. Example:
    # https://www.elastic.co/guide/en/apm/agent/python/master/api.html#client-api-capture-exception
    #elasticapm.set_user_context(username=result['username'], email=result['email'], user_id=result['id']) #TODO DOESNT WORK

    # Attach custom contextual data to the current transaction and errors. Supported frameworks will automatically attach information about the HTTP request and the logged in user. You can attach further data using this function.
    # https://www.elastic.co/guide/en/apm/agent/python/master/api.html#client-api-capture-exception
    #elasticapm.set_custom_context({'billing_amount': result['cost_spend'] * result['item_count']}) #TODO DOESNT WORK

    # Get the id of the current transaction.
    transaction_id = elasticapm.get_transaction_id()
    logger.info('Current transaction_id: ' + str(transaction_id))

    # Get the trace_id of the current transaction’s trace.
    trace_id = elasticapm.get_trace_id()
    logger.info('Current trace_id: ' + str(trace_id))

    # Get the id of the current span.
    span_id = elasticapm.get_span_id()
    logger.info('Current span_id: ' + str(span_id))

    # As you can se the logging from the root logger has been added to the apm_client
    apm_client.logger.root.handlers[0].records

    # As you can also see the apm_client is also accessable from the elasticapm
    elasticapm.Client.logger.root.handlers[0].records == apm_client.logger.root.handlers[0].records

    return result

