import sqlite3
import time


class DataManager(object):

    def __init__(self):
        super(DataManager, self).__init__()
        self.__cursor = sqlite3.connect("test.db").cursor()
        # 在meta_table表中存放数据表的类型信息和创建时间信息
        self.__cursor.execute("select count(*) from sqlite_master where type='table' and name='meta_table'")
        if self.__cursor.fetchall()[0][0] <= 0:  # 数据库中没有meta_table则新建一个
            self.__cursor.execute("create table meta_table "
                                  "(name text primary key not null, type text not null, create_time integer not null);")
            self.__cursor.connection.commit()

    def get_tables(self) -> list:
        """获取当前数据表中所有表名"""
        self.__cursor.execute("select name from sqlite_master where type='table' order by name")
        return [t[0] for t in self.__cursor.fetchall()]

    def get_my_tables(self, my_type: str) -> list:
        """根据表的类型获取数据表名"""
        if my_type == 'all':
            sql = "select name from meta_table"
        else:
            sql = f"select name from meta_table where type = '{my_type}'"
        self.__cursor.execute(sql)
        return [t[0] for t in self.__cursor.fetchall()]

    def get_columns(self, table_name: str) -> list:
        self.__cursor.execute('pragma table_info(' + table_name + ')')
        return self.__cursor.fetchall()

    def get_column_types(self, table_name: str) -> dict:
        """返回一个字典：列名->列数据类型"""
        self.__cursor.execute('pragma table_info(' + table_name + ')')
        columns = self.__cursor.fetchall()
        return {c[1]: c[2] for c in columns}

    def create_table(self, table_type: str, table_name: str, table_columns: list):
        """新建一张类型为table_type，名为table_name的表，各列列名由table_columns定义，"""
        # 先加入meta_table
        self.__cursor.execute(
            f"insert into meta_table (name, type, create_time) "
            f"values ('{table_name}', '{table_type}', {int(time.time())});")  # 时间戳为秒级
        # 然后创建表格
        self.__cursor.execute('create table {name} (id integer primary key autoincrement, {columns});'
                              .format(name=table_name, columns=",".join(c + ' text' for c in table_columns)))
        self.__cursor.connection.commit()

    def insert_data(self, table_name: str, columns: list, rows: list):
        """向table_name表中插入一行或多行数据，这里rows中每一个元组都按照columns指定的顺序排列"""
        sql = 'insert into {name} ({columns}) values {rows};' \
            .format(name=table_name, columns=', '.join(columns),
                    rows=', '.join("(" + ", ".join("'" + d + "'" for d in r) + ")" for r in rows))
        self.__cursor.execute(sql)
        self.__cursor.connection.commit()
