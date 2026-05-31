import pymysql

class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = pymysql.connect(host='localhost',
                                          port=3306,
                                          user='root',
                                          password='root',
                                          database='shoes',
                                          cursorclass=pymysql.cursors.DictCursor)
        return self.connection

    def close(self):
        self.connection.close()

    def fetchall(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            cursor.close()

    def fetchone(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except Exception as e:
            print(e)
        finally:
            cursor.close()

    def execute(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            cursor.commit()
            return cursor.lastrowid
        except Exception as e:
            print(e)
        finally:
            cursor.close()