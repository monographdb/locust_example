import gevent
from gevent import monkey; 
monkey.patch_all()

from sqlalchemy import NullPool, create_engine, exc, select, text, QueuePool
from locust import TaskSet, User, constant_throughput, events, task, between

import client
import config


class MyLocust(User):
    abstract = True  # dont instantiate this as an actual user when running Locust
    def __init__(self, environment):
        super().__init__(environment)
        if config.USE_PREPARE_STMT:
            self.client = client.PrepareStmtClient()
        else:
            self.client = client.PoolClient()


class QueryUser(MyLocust):
    # wait_time = between(0.1, 1)

    @task
    def test_my_query(self):
        pass


    def on_start(self):
        pass
        

    def on_stop(self):
        pass        
        
