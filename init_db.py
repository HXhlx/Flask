import os
import re
from mysql.connector import connect
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ['DB_HOST']
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']

cnx = connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD)
cursor = cnx.cursor()
cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
cursor.close()
cnx.close()

cnx = connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
cursor = cnx.cursor()

with open('bookstore.sql', 'r', encoding='utf-8') as f:
    raw = f.read()

lines = raw.split('\n')
statements = []
buf = []
for line in lines:
    stripped = line.strip()
    if not stripped:
        continue
    if stripped.startswith('--'):
        continue
    if stripped.startswith('/*') and stripped.endswith('*/'):
        continue
    if stripped.startswith('/*!'):
        continue
    if stripped in ('LOCK TABLES addmembers WRITE;',
                    'LOCK TABLES admin WRITE;',
                    'LOCK TABLES buybook WRITE;',
                    'LOCK TABLES leasebook WRITE;',
                    'LOCK TABLES members WRITE;',
                    'LOCK TABLES newbook WRITE;',
                    'LOCK TABLES oldbook WRITE;',
                    'LOCK TABLES orderbook WRITE;'):
        continue
    if stripped == 'UNLOCK TABLES;':
        continue
    if re.match(r'/\*!\d+', stripped):
        continue
    buf.append(line)
    if stripped.endswith(';'):
        stmt = '\n'.join(buf).strip()
        if stmt:
            statements.append(stmt)
        buf = []

for stmt in statements:
    try:
        cursor.execute(stmt)
        cnx.commit()
    except Exception as e:
        pass

cursor.close()
cnx.close()
print("Done")
