import os
import sys
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
max_tokens = 2000

query = sys.argv[1]

metrics_summary = """
Configureation of dbt model: **Model 1** version: 2models: - name: analytics__orders description: order statistics columns: - name: order_id description: unique id for each orders created meta: dimension: type: int metrics: total_orders_created_per_date: type: count lable: Total orders created. Given this, and only this, configuration, could I find an answer to my question:
"""

table_summary = """
Chema for tables: **Table 1: customers**| Column Name | Data Type | Description || --- | --- | --- || customer_id | SERIAL | Unique identifier for each customer || name | VARCHAR(50) | The customer's name || email | VARCHAR(100) | The customer's email address || address | TEXT | The customer's address |**Table 2: orders**| Column Name | Data Type | Description || --- | --- | --- || order_id | SERIAL | Unique identifier for each order || customer_id | INTEGER | The ID of the customer who placed the order || order_date | DATE | The date the order was placed || total_amount | DECIMAL(10,2) | The total amount of the order || status | VARCHAR(20) | The status of the order (e.g. "pending", "shipped", "delivered") |. dbt metrics layer: version: 2models:  - name: analytics__orders    description: order statistics    columns:      - name: order_id        description: unique id for each orders created        meta:          dimension:            type: int          metrics:            orders_created:              type: count              lable: Total orders created. As a senior analyst, given the above schemas and data, write a detailed and correct Postgres sql query to answer the analytical question:
"""

prompt = f"""
{metrics_summary} "{query}", and in what metric would that be?
Give me the metrics name.
"""

resp = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt,
  max_tokens=max_tokens,
  temperature=0
)
print("Question:\n")
print(query)
print("\nPotential metrics layer:")
print(resp["choices"][0]["text"])

prompt = f"""
{table_summary}

"{query}"

Only output the sql queries, each printed in a codeblock.
"""

resp = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt,
  max_tokens=max_tokens,
  temperature=0
)
sql_query = resp["choices"][0]["text"]
print(sql_query)
#print("\nSepperated queries\n")

# Split the string into individual query strings
query_strings = sql_query.split("?")

# Remove the first (empty) element of the resulting list
query_strings = query_strings[1:]

# Extract the SQL code from each query string
queries = []
for query_str in query_strings:
    sql = query_str.split("?")[1].strip()
    if sql.endswith(";"):
        queries.append(sql)
    else:
        queries.append(sql + ";")

    print(queries)

### Postgres part
import psycopg2

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="example_db",
    user="postgres",
    password="postgres"
)

# Open a cursor to perform database operations
cur = conn.cursor()
results = ""
# Loop through the queries and execute them
for query in queries:
    cur.execute(query)
    for row in cur.fetchall():
        results = results + str(row) + "\n"
    results = results + ": \n"

# Close the cursor and connection
cur.close()
conn.close()

prompt = f"""
And all my query output: {results}
Please print this otput in a nice way, for all results.
"""

resp = openai.Completion.create(
  model="text-davinci-003",
  prompt=prompt,
  max_tokens=max_tokens,
  temperature=0
)
print("\nResult from database:")
print(resp["choices"][0]["text"])
