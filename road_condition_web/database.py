import sqlite3
from sqlite3 import Error


db_file = './roaddata.db'

# 数据库通用工具类
# 获取连接

def get_db_conn(db_file):
    conn=None
    try:
        conn=sqlite3.connect(db_file)
    except Error as e:
        print(e)
    if conn is not None:
        return conn


# 关闭资源
def close_db_conn(cur,conn):
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()


if __name__ == "__main__":
    conn = get_db_conn(db_file)
    cur = conn.cursor()
    sql = '''CREATE TABLE ROADCONDITION(
                              id INTEGER PRIMARY KEY, 
                              time VARCHAR,
                              lng FLOAT,
                              lat FLOAT,
                              condition TEXT
                                    );'''
    # sql="drop table ROADCONDITION"
    try:
        cur.execute(sql)
        print("创建表成功")
    except Exception as e:
        print(e)
        print("创建表失败")
    finally:
        close_db_conn(cur,conn)