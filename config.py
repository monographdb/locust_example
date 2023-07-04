

USER = 'sysb'
PASSWORD = 'sysb'

IP_ADDR = "127.0.0.1"
PORT = 3317
# database name
TS_DB_NAME = "test"

# False: Create a connection from connection pool. And dosen't use prepare_stmt. 
# True: Create a long connection. Use prepare_stmt.
USE_PREPARE_STMT = True

POOL_SIZE = 300
POOL_RECYCLE = -1

connection_path = "mariadb+mysqlconnector://" + USER  + ":" + PASSWORD + "@" + IP_ADDR + ":" + str(PORT) + "/" + TS_DB_NAME