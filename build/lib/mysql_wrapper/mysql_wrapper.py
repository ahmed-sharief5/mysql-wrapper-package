import mysql.connector
from mysql.connector import Error
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MySQLWrapper:
    """
    A wrapper class to handle MySQL database operations such as connect, insert, update, delete, and retrieve data.
    """

    def __init__(self, host, user, password, database, idle_timeout=300):
        """
        Initializes the MySQLWrapper instance with database connection details.
        
        :param host: The MySQL server host.
        :param user: The MySQL user.
        :param password: The MySQL user's password.
        :param database: The name of the MySQL database.
        :param idle_timeout: Time in seconds after which idle connection will be closed.
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.last_active_time = time.time()
        self.idle_timeout = idle_timeout
        self.connect()

    def connect(self):
        """
        Establishes a connection to the MySQL database.
        """
        try:
            if self.connection and self.connection.is_connected():
                logger.info("Using existing MySQL connection")
            else:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                if self.connection.is_connected():
                    logger.info("Connected to MySQL database")
                self.last_active_time = time.time()
        except Error as e:
            logger.error(f"Error while connecting to MySQL: {e}")
            raise e

    def is_connected(self):
        """
        Checks if the connection to the MySQL database is established.
        
        :return: True if the connection is established, False otherwise.
        """
        self._handle_idle_connection()
        return self.connection is not None and self.connection.is_connected()

    def _handle_idle_connection(self):
        """
        Handles idle connection by checking if it has been idle for too long and closing it if necessary.
        """
        if self.connection and self.connection.is_connected():
            idle_time = time.time() - self.last_active_time
            if idle_time > self.idle_timeout:
                logger.info("Connection has been idle for too long. Closing connection.")
                self.close()

    def _reconnect_if_needed(self):
        """
        Reconnects to the database if the connection is not established.
        """
        if not self.is_connected():
            logger.info("Reconnecting to the database...")
            self.connect()

    def _execute_query(self, query, params=None):
        """
        Executes a query and manages connection retries.

        :param query: SQL query to execute.
        :param params: Parameters to pass to the SQL query.
        :return: Cursor object after executing the query.
        """
        self._reconnect_if_needed()
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.last_active_time = time.time()
            return cursor
        except Error as e:
            logger.error(f"Error while executing query: {e}")
            self.connection.rollback()
            raise e

    def insert_one(self, table, data):
        """
        Inserts a single record into the specified table.
        
        :param table: The name of the table to insert the record into.
        :param data: A dictionary representing the record to insert.
        """
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            cursor = self._execute_query(query, tuple(data.values()))
            self.connection.commit()
            logger.info(f"Inserted {cursor.rowcount} row(s) into {table}")
            return cursor.lastrowid
        except Error as e:
            logger.error(f"Error while inserting data: {e}")
            raise e

    def insert_many(self, table, data_list):
        """
        Inserts multiple records into the specified table.
        
        :param table: The name of the table to insert the records into.
        :param data_list: A list of dictionaries, each representing a record to insert.
        :raises ValueError: If the data_list is empty.
        """
        if not data_list:
            raise ValueError("The data_list is empty.")
        
        try:
            columns = ', '.join(data_list[0].keys())
            placeholders = ', '.join(['%s'] * len(data_list[0]))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            values = [tuple(data.values()) for data in data_list]

            cursor = self._execute_query(query, values)
            self.connection.commit()
            logger.info(f"Inserted {cursor.rowcount} rows into {table}")
            return cursor.lastrowid
        except Error as e:
            logger.error(f"Error while inserting bulk data: {e}")
            raise e

    def update(self, table, data, where_clause):
        """
        Updates records in the specified table based on the provided where_clause.
        
        :param table: The name of the table to update.
        :param data: A dictionary representing the columns and their new values.
        :param where_clause: The WHERE clause to filter which records to update.
        """
        try:
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            cursor = self._execute_query(query, tuple(data.values()))
            self.connection.commit()
            logger.info(f"Updated {cursor.rowcount} row(s) in {table}")
            return cursor.rowcount
        except Error as e:
            logger.error(f"Error while updating data: {e}")
            raise e

    def delete(self, table, where_clause):
        """
        Deletes records from the specified table based on the provided where_clause.
        
        :param table: The name of the table to delete records from.
        :param where_clause: The WHERE clause to filter which records to delete.
        """
        try:
            query = f"DELETE FROM {table} WHERE {where_clause}"
            cursor = self._execute_query(query)
            self.connection.commit()
            logger.info(f"Deleted {cursor.rowcount} row(s) from {table}")
            return cursor.rowcount
        except Error as e:
            logger.error(f"Error while deleting data: {e}")
            raise e

    def get(self, table, columns="*", where_clause=None):
        """
        Retrieves data from the specified table based on the provided where_clause.
        
        :param table: The name of the table to retrieve data from.
        :param columns: A list of columns to retrieve, or "*" for all columns.
        :param where_clause: Optional WHERE clause to filter results.
        :return: A list of tuples representing the retrieved rows.
        """
        try:
            if isinstance(columns, list):
                columns = ', '.join(columns)
            query = f"SELECT {columns} FROM {table}"
            if where_clause:
                query += f" WHERE {where_clause}"
            cursor = self._execute_query(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            logger.error(f"Error while retrieving data: {e}")
            return None

    def execute_query(self, query, params=None):
        """
        Executes a raw SQL query. This method can be used for any custom query, including SELECT, INSERT, UPDATE, and DELETE.
        
        :param query: The raw SQL query to execute.
        :param params: Optional parameters for the query (used with parameterized queries).
        :return: The result of the query for SELECT statements, or None for other queries.
        """
        try:
            cursor = self._execute_query(query, params)
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
                logger.info(f"Query executed successfully: {cursor.rowcount} row(s) affected")
        except Error as e:
            logger.error(f"Error while executing query: {e}")
            return None

    def close(self):
        """
        Closes the connection to the MySQL database.
        """
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")

