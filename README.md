### Asynchronous Tasks with FastAPI and Celery

Example of how to handle background processes with FastAPI, Celery, and Docker.

### Quick Start

Spin up the containers:

```sh
$ docker-compose up -d --build
```

Then check services are working:

```sh
$ docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS                                       NAMES
c887d5256561   mlapi_worker   "celery -A worker.ce…"   8 minutes ago   Up 8 minutes                                               mlapi_worker_1
bfda537b908a   mlapi_web      "uvicorn main:app --…"   8 minutes ago   Up 8 minutes   0.0.0.0:8004->8000/tcp, :::8004->8000/tcp   mlapi_web_1
19feb6a993e4   redis:7        "docker-entrypoint.s…"   8 minutes ago   Up 8 minutes   6379/tcp                                    mlapi_redis_1
```

Then send requests:

```sh
curl -X 'POST' 'http://127.0.0.1:8004/predict' -H 'accept: application/json' -H 'Content-Type: application/json' -d '[{"data": "{\"CLIENT_IP\": \"188.138.92.55\", \"CLIENT_USERAGENT\": NaN, \"REQUEST_SIZE\": 166, \"RESPONSE_CODE\": 404, \"MATCHED_VARIABLE_SRC\": \"REQUEST_URI\", \"MATCHED_VARIABLE_NAME\": NaN, \"MATCHED_VARIABLE_VALUE\": \"//tmp/20160925122692indo.php.vob\", \"EVENT_ID\": \"AVdhXFgVq1Ppo9zF5Fxu\"}"}, {"data": "{\"CLIENT_IP\": \"93.158.215.131\", \"CLIENT_USERAGENT\": \"Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0\", \"REQUEST_SIZE\": 431, \"RESPONSE_CODE\": 302, \"MATCHED_VARIABLE_SRC\": \"REQUEST_GET_ARGS\", \"MATCHED_VARIABLE_NAME\": \"url\", \"MATCHED_VARIABLE_VALUE\": \"http://www.galitsios.gr/?option=com_k2\", \"EVENT_ID\": \"AVdcJmIIq1Ppo9zF2YIp\"}"}]'
```

Service will create Celery task and send you unique identifier:

```sh
{"task_id":"bd89d4e7-4d26-4348-be0b-0cbc55683532"}
```

 You can get results using this id by sending:

```sh
curl http://localhost:8004/tasks/bd89d4e7-4d26-4348-be0b-0cbc55683532
```

And receive results:

```sh
[{"EVENT_ID":"AVdcJmIIq1Ppo9zF2YIp","LABEL_PRED":"0"},{"EVENT_ID":"AVdcJmIIq1Ppo9zF2YIp","LABEL_PRED":"0"}]
```

### Architecture from here:
https://testdriven.io/blog/fastapi-and-celery/
https://github.com/testdrivenio/fastapi-celery

### Multiclass classification idea from:
https://scikit-learn.org/stable/modules/multiclass.html
https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier

