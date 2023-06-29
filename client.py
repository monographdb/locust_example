import gevent
from gevent import monkey; 
monkey.patch_all()

import random
import time
import config
import mysql.connector

from sqlalchemy import NullPool, create_engine, exc, select, text, QueuePool
from locust import TaskSet, User, constant_throughput, events, task, between
# from sqlalchemy.ext.asyncio import create_async_engine



def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

    
"""
sqlalchemy doc
    https://docs.sqlalchemy.org/en/20/core/pooling.html
"""    
@singleton
class ConnectionPool(object):
    def __init__(self):
        self.engine = create_engine(config.connection_path, pool_size=config.POOL_SIZE, pool_recycle=config.POOL_RECYCLE)

    def pool(self):
        return self.engine.pool

# Thread Safe ?
if config.USE_PREPARE_STMT == False:
    print("Initialize Connection Pool")
    _p = ConnectionPool().pool()


"""
sqlalchemy doc
    https://docs.sqlalchemy.org/en/20/core/pooling.html
"""
# engine = create_engine(config.connection_path, pool_size=300, pool_recycle=-1)
# pool = engine.pool
# engine = create_engine("mariadb+pymysql://sysb:sysb@127.0.0.1:3317/test", poolclass=NullPool)


"""
Mysql engine
# engine = create_engine("mysql+pymysql://lokax:12345@127.0.0.1:3306/test", pool_size=300, pool_recycle=-1)
# pool = engine.pool
# engine = create_engine("mysql+pymysql://lokax:12345@127.0.0.1:3306/test", poolclass= NullPool)
"""

"""
### Async engine
# async_engine = create_async_engine("mariadb+asyncmy://sysb:sysb@127.0.0.1:3317/test", pool_size=300, pool_recycle=-1)
"""


class MyClient(object):
    def __init__(self):
        self.rid = random.random()

    def execute(self, operation, params=(), multi=False):
        pass



class PrepareStmtClient(MyClient):

    """
    MysqlCursorPreared doc
        https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursorprepared.html
    """
    def __init__(self):
        assert(config.USE_PREPARE_STMT == True)
        super().__init__()
        self.cnx = mysql.connector.Connect(user=config.USER, password=config.PASSWORD, database=config.TS_DB_NAME, host=config.IP_ADDR, port=config.PORT)
        self.curprep = self.cnx.cursor(prepared=config.USE_PREPARE_STMT)

        # Prepare Stmt
        # stmt = "SELECT * FROM test.t1 WHERE i=%s;"
        # self.curprep.execute(stmt)

        # self.cur = self.cnx.cursor(buffered=True)
        
        ### Prepare
        # cursor.execute("prepare test from 'select * from test.t1 where i=?;'")
        
        # self.conn = pool.connect()
        # self.engine = create_engine("mariadb+pymysql://mono:mono@127.0.0.1:3317/test", poolclass=sqlalchemy.pool.SingletonThreadPool)
        # self.engine = create_engine("mariadb+pymysql://mono:mono@127.0.0.1:3317/test", poolclass=NullPool)

    def __del__(self):
        self.curprep.close()
        self.cnx.close()


    """
        https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursorprepared.html
    """
    
    def execute(self, operation, params=(), multi=False):
        try:
            request_meta = {
                "request_type": "prepare_execute",
                "name": operation,
                "start_time": time.time(),
                "response_length": 0,  # calculating this for an xmlrpc.client response would be too hard
                "response": None,
                "context": {},  # see HttpUser if you actually want to implement contexts
                "exception": None,
                "response_time": 0
            }

            ### Execute stmt           
            self.curprep.execute(operation, params, multi)
            rowset = self.curprep.fetchall()
            self.cnx.commit()
            
            
            request_meta["response"] = "Ok"
            request_meta["response_length"] = len(rowset)
            # request_meta["response"] = rowset

        except Exception as e:
            request_meta["exception"] = e

        request_meta["response_time"] = (time.time() -   request_meta["start_time"]) * 1000
        events.request.fire(**request_meta)
    

class PoolClient(MyClient):

    def __init__(self):
        super().__init__()

    """
    DBAPI doc
        https://peps.python.org/pep-0249
    """
    def execute(self, operation, unused1=(), multi=False):
        try:
            request_meta = {
                "request_type": "execute_from_pool",
                "name": operation,
                "start_time": time.time(),
                "response_length": 0,  # calculating this for an xmlrpc.client response would be too hard
                "response": None,
                "context": {},  # see HttpUser if you actually want to implement contexts
                "exception": None,
                "response_time": 0
            }

            # Return connection from pool
            conn = ConnectionPool().pool().connect()
            # conn = pool.connect()
            cursor = conn.cursor()
            cursor.execute(operation)
            rowset = cursor.fetchall()
            conn.commit()



            # desc = cursor.description()
            # row_count = cursor.rowcount()
        
            request_meta["response"] = "Ok!"
            request_meta["response_length"] = len(rowset)
            # request_meta["response"] = rowset

        except Exception as e:
            request_meta["exception"] = e
        finally:
            # Close cursor and connection
            cursor.close()
            conn.close()
            request_meta["response_time"] = (time.time() -   request_meta["start_time"]) * 1000
            events.request.fire(**request_meta)