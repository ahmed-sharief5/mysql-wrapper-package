import mysql.connector
from mysql.connector import Error

class MySQLWrapper:
    """
    A wrapper class to handle MySQL database operations such as connect, insert, update, delete, and retrieve data.
    """

    def __init__(self, host, user, password, database):
        """
        Initializes the MySQLWrapper instance with database connection details.
        
        :param host: The MySQL server host.
        :param user: The MySQL user.
        :param password: The MySQL user's password.
        :param database: The name of the MySQL database.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """
        Establishes a connection to the MySQL database.
        
        :raises Exception: If the connection cannot be established.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    def is_connected(self):
        """
        Checks if the connection to the MySQL database is established.
        
        :return: True if the connection is established, False otherwise.
        """
        if self.connection:
            return self.connection.is_connected()
        return False

    def insert_one(self, table, data):
        """
        Inserts a single record into the specified table.
        
        :param table: The name of the table to insert the record into.
        :param data: A dictionary representing the record to insert.
        :raises Exception: If the connection is not established.
        """
        if not self.connection:
            raise Exception("Connection not established. Call connect() first.")
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            print(f"Inserted {cursor.rowcount} row(s) into {table}")
        except Error as e:
            print(f"Error while inserting data: {e}")

    def insert_many(self, table, data_list):
        """
        Inserts multiple records into the specified table.
        
        :param table: The name of the table to insert the records into.
        :param data_list: A list of dictionaries, each representing a record to insert.
        :raises Exception: If the connection is not established.
        :raises ValueError: If the data_list is empty.
        """
        if not self.connection:
            raise Exception("Connection not established. Call connect() first.")
        if not data_list:
            raise ValueError("The data_list is empty.")
        try:
            columns = ', '.join(data_list[0].keys())
            placeholders = ', '.join(['%s'] * len(data_list[0]))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            values = [tuple(data.values()) for data in data_list]

            cursor = self.connection.cursor()
            cursor.executemany(query, values)
            self.connection.commit()
            print(f"Inserted {cursor.rowcount} rows into {table}")
        except Error as e:
            print(f"Error while inserting bulk data: {e}")

    def update(self, table, data, where_clause):
        """
        Updates records in the specified table based on the provided where_clause.
        
        :param table: The name of the table to update.
        :param data: A dictionary representing the columns and their new values.
        :param where_clause: The WHERE clause to filter which records to update.
        :raises Exception: If the connection is not established.
        """
        if not self.connection:
            raise Exception("Connection not established. Call connect() first.")
        try:
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            cursor = self.connection.cursor()
            cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            print(f"Updated {cursor.rowcount} row(s) in {table}")
        except Error as e:
            print(f"Error while updating data: {e}")

    def delete(self, table, where_clause):
        """
        Deletes records from the specified table based on the provided where_clause.
        
        :param table: The name of the table to delete records from.
        :param where_clause: The WHERE clause to filter which records to delete.
        :raises Exception: If the connection is not established.
        """
        if not self.connection:
            raise Exception("Connection not established. Call connect() first.")
        try:
            query = f"DELETE FROM {table} WHERE {where_clause}"
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            print(f"Deleted {cursor.rowcount} row(s) from {table}")
        except Error as e:
            print(f"Error while deleting data: {e}")

    def get(self, table, columns="*", where_clause=None):
        """
        Retrieves data from the specified table based on the provided where_clause.
        
        :param table: The name of the table to retrieve data from.
        :param columns: A list of columns to retrieve, or "*" for all columns.
        :param where_clause: Optional WHERE clause to filter results.
        :return: A list of tuples representing the retrieved rows.
        :raises Exception: If the connection is not established.
        """
        if not self.connection:
            raise Exception("Connection not established. Call connect() first.")
        try:
            if isinstance(columns, list):
                columns = ', '.join(columns)
            query = f"SELECT {columns} FROM {table}"
            if where_clause:
                query += f" WHERE {where_clause}"
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error while retrieving data: {e}")
            return None
        
    def execute_query(self, query, params=None):
        """
        Executes a raw SQL query. This method can be used for any custom query, including SELECT, INSERT, UPDATE, and DELETE.
        
        :param query: The raw SQL query to execute.
        :param params: Optional parameters for the query (used with parameterized queries).
        :return: The result of the query for SELECT statements, or None for other queries.
        :raises Exception: If the connection is not established.
        """
        if not self.connection:
            raise Exception("Connection not established. Call connect() first.")
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                return result
            else:
                self.connection.commit()
                print(f"Query executed successfully: {cursor.rowcount} row(s) affected")
        except Error as e:
            print(f"Error while executing query: {e}")
            return None

    def close(self):
        """
        Closes the connection to the MySQL database.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")