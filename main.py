#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import os
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

# Load dotenv
python_env = os.getenv('PYTHON_ENV') or 'development'
dotenv_path = os.path.join(
    os.path.dirname(__file__),
    '.env.' + python_env
)
dotenv.load_dotenv(dotenv_path)

# Add the handler to the root logger
# https://www.elastic.co/guide/en/apm/agent/python/master/log-correlation.html#logging

# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
handler = logging.StreamHandler()
handler.addFilter(LoggingFilter())

# Create formatters and add it to handlers
format = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(format)

# Add handlers to the logger
logger.addHandler(handler)

# Create the fast API app
app = FastAPI()

# Creating middleware
# https://www.elastic.co/guide/en/apm/agent/python/master/starlette-support.html
settings = {
    'SERVER_URL':os.environ.get('APM_SERVER_URL'),
    'SERVICE_NAME':os.environ.get('APM_SEVICE_NAME'),
    'SECRET_TOKEN':os.environ.get('APM_SECRET_TOKEN'),
    'CAPTURE_BODY':'all',
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
    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message', extra=result)
    logger.critical('This is a critical message')
    logger.exception("This is an exception")
    
    #Capture an arbitrary exception by calling capture_exception:
    try:
        1 / 0
    except ZeroDivisionError:
        apm_client.capture_exception()

    # As you can se the logging from the root logger has been added to apm_client.logger.root.handlers[0].records

    # Log a generic message with capture_message:
    apm_client.capture_message('hello, world!')

    # Alternatively, a parameterized message as a dictionary.
    apm_client.capture_message(param_message={
        'message': 'Billing process for %s succeeded. Amount: %s',
        'params': (result['id'], result['billing_amount']),
    })

    # Attach labels to the the current transaction and errors.
    # https://www.elastic.co/guide/en/apm/agent/python/master/api.html#client-api-capture-exception
    elasticapm.label(ecommerce=True, dollar_value=float(result['cost_spend']))

    # Attach information about the currently logged in user to the current transaction and errors. Example:
    # https://www.elastic.co/guide/en/apm/agent/python/master/api.html#client-api-capture-exception
    elasticapm.set_user_context(username=result['username'], email=result['email'], user_id=result['id'])

    # Attach custom contextual data to the current transaction and errors. Supported frameworks will automatically attach information about the HTTP request and the logged in user. You can attach further data using this function.
    # https://www.elastic.co/guide/en/apm/agent/python/master/api.html#client-api-capture-exception
    elasticapm.set_custom_context({'billing_amount': result['cost_spend'] * result['item_count']})

    # Get the id of the current transaction.
    transaction_id = elasticapm.get_transaction_id()
    logging.info('Current transaction_id: ' + str(transaction_id))

    # Get the trace_id of the current transaction’s trace.
    trace_id = elasticapm.get_trace_id()
    logging.info('Current trace_id: ' + str(trace_id))

    # Get the id of the current span.
    span_id = elasticapm.get_span_id()
    logging.info('Current span_id: ' + str(span_id))

    return result

