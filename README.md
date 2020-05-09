## Roadmap
Vision:
> Deploy a modern `fastapi` API template app with build in preformance monitoring and error logging using `elastic APM`, with the press of a button using AWS `CloudFormation`. 

- [x] Integrate fast API middlware for APM logging
- [x] docker-compose for ELK and APM stack
- [x] Example endpoints and data
- [x] Tests in pytest
- [ ] Add codeship support and system tests
- [ ] Cloudformation template for FastAPI and ELK. 
- [ ] Add a Launch Stack AWS button to the API
- [ ] Create a Elastic search example endpoint in fast API 

## Introduction

This project aims to show how APS logging and dashboard can be integrated with the excelent `fastAPI` framework created by my personal hero [tiangolo](https://github.com/tiangolo). 

Backend related projects will always integrate some essential services, e.g.:

- Sentry for logging [cost](https://sentry.io/pricing)
- Newrelic for performance monitor, see [cost](https://newrelic.com/application-monitoring/pricing)
- APS and the ELK stack, it's open-source and **free**

From the elastic [website](https://www.elastic.co/observability)
> Bring your logs, metrics, and APM traces together at scale in a single stack so you can monitor and react to events happening anywhere in your environment. And it's free and open.

![apm-architecture](https://www.elastic.co/guide/en/apm/get-started/current/images/apm-architecture-cloud.png)

## Getting started

This project is a demo to show feature and usage of elastic apm, based on docker and flask.

1. Install dependencies. 
```
make local-setup-environment
```

2. Run EKS dashboard and fastAPI service. 
```
make local-run
```

3. Send some data to the API:
```
for i in $(seq 100); do http :8000/checkout email="${i}@email.domain" username="${i}" cost_spend="${i}" item_count="1"; done
```

4. See preformance metrics and logging in `Kibana`. 
```
http://localhost:5601/app/kibana
```

### Screenshot

![](screenshots/transaction.png)

### Reference
- [APM overview](https://www.elastic.co/guide/en/apm/get-started/7.6/index.html)
- [Fast API support | APM Python Agent](https://www.elastic.co/guide/en/apm/agent/python/master/starlette-support.html)
