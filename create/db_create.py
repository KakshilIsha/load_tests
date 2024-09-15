import psycopg2
from psycopg2.extras import execute_values
import json
import random
from faker import Faker

# Connection parameters
host = '3.110.145.75'
dbname = 'postgres'
user = 'postgres'
password = 'ishapostgres'

# Create a connection to PostgreSQL
conn = psycopg2.connect(
    host=host,
    dbname=dbname,
    user=user,
    password=password
)

# Create a cursor object
cursor = conn.cursor()

# SQL to create two tables
create_table_sql_1 = """
CREATE TABLE IF NOT EXISTS read_table (
    id SERIAL PRIMARY KEY,
    col1 VARCHAR(255),
    col2 INTEGER,
    col3 DECIMAL,
    col4 TEXT,
    col5 BOOLEAN,
    col6 DATE,
    col7 TIMESTAMP,
    col8 VARCHAR(255),
    col9 INTEGER,
    col10 VARCHAR(255),
    col11 TEXT,
    col12 VARCHAR(255),
    col13 DECIMAL,
    col14 TEXT,
    col15 JSONB
);
"""

create_table_sql_2 = """
CREATE TABLE IF NOT EXISTS write_table (
    id SERIAL PRIMARY KEY,
    col1 VARCHAR(255),
    col2 INTEGER,
    col3 DECIMAL,
    col4 TEXT,
    col5 BOOLEAN,
    col6 VARCHAR(255),
    col7 INTEGER,
    col8 DECIMAL,
    col9 TEXT,
    col10 JSONB
);
"""

# Execute table creation
cursor.execute(create_table_sql_1)
cursor.execute(create_table_sql_2)
conn.commit()



# Faker library to generate random data
fake = Faker()

# Function to generate random JSON with 30 key-value pairs
def generate_json_data():
    return {f"key_{i}": fake.word() for i in range(1, 31)}

# Insert 100K rows into the read_table
data_read = [
    (
        fake.word(),
        random.randint(1, 1000),
        random.uniform(1.0, 1000.0),
        fake.text(),
        fake.boolean(),
        fake.date(),
        fake.date_time(),
        fake.word(),
        random.randint(1, 1000),
        fake.word(),
        fake.text(),
        fake.word(),
        random.uniform(1.0, 1000.0),
        fake.text(),
        json.dumps(generate_json_data())  # JSON data
    ) for _ in range(100000)
]

# Efficient batch insert for read_table
insert_sql_read = """
    INSERT INTO read_table (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15)
    VALUES %s
"""
execute_values(cursor, insert_sql_read, data_read)
conn.commit()




# Insert 10K rows into the write_table
data_write = [
    (
        fake.word(),
        random.randint(1, 1000),
        random.uniform(1.0, 1000.0),
        fake.text(),
        fake.boolean(),
        fake.word(),
        random.randint(1, 1000),
        random.uniform(1.0, 1000.0),
        fake.text(),
        json.dumps(generate_json_data())  # JSON data
    ) for _ in range(10000)
]

# Efficient batch insert for write_table
insert_sql_write = """
    INSERT INTO write_table (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10)
    VALUES %s
"""
execute_values(cursor, insert_sql_write, data_write)
conn.commit()

# Read 100K rows from read_table
cursor.execute("SELECT * FROM read_table LIMIT 100")
rows = cursor.fetchall()
print(f"Fetched {len(rows)} rows from read_table")
print(rows)

# Write 10K rows to write_table
cursor.execute("SELECT * FROM write_table LIMIT 100")
rows = cursor.fetchall()
print(f"Fetched {len(rows)} rows from write_table")
print(rows)

# Close the cursor and connection
cursor.close()
conn.close()
