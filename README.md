---
title: Locust example
summary: Learn how to use locust to test the database.
---

# locust test

This document describes how to use locust to test the database

## Installation
```shell
pip install pymysql mysql-connector sqlalchemy gevent locust
```

## How to let the client run your query

**For now we have two custom clients**
- PoolClient: Acquire a connection from connection pool. And dosen't use prepare statment.
- PrepareStmtClient: Create a long connection. Use prepare statment.


**Usage**
- When USE_PREPARE_STMT is true, we will use PrepareStmtClient.
- PoolClient: `self.client.execute("SELECT * FROM test.sbtest1 WHERE id>1 AND id<100;")`
- PrepareStmtClient: `self.client.execute("SELECT * FROM test.sbtest1 WHERE id > ? AND id < ?;", (1, 100, ))`

## How to run locust
1. You can specify information such as IP address and Port number in the config.py file
```config.py
USER = 'sysb'
PASSWORD = 'sysb'

IP_ADDR = "127.0.0.1"
PORT = 3317
# database name
TS_DB_NAME = "test"

# False: Create a connection from connection pool. And dosen't use prepare_stmt.
# True: Create a long connection. Use prepare_stmt.
USE_PREPARE_STMT = False
```


 2. Run `bash start_worker.sh ${WorkerNumber}`. `${Workernumber}` indicates how many Locust processes will be created. We will have one master process and ${WorkerNumber} workers processes. If you want to run Locust with multiple machines, please refer to [how to run distributed](https://docs.locust.io/en/stable/running-distributed.html#running-distributed ).

 3. Wait a few seconds until all workers are connected to the master.

 4. Open http://your_locust_master_ip:8089/ and start swarming.

 5. When you don't want to test. First click `Stop` buttom on website. Then Run `pkill -9 locust` to kill locust processes.


## More about locust
**If you want to knonw**
```python
@task means ... 
@task(2) means ... 
on_start(self) means ...
```
See [how to write locust file](https://docs.locust.io/en/stable/writing-a-locustfile.html). 

