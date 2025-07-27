import sqlite3

# 1. Connect to your database (it creates the file if it doesn't exist)
conn = sqlite3.connect("your_database.db")  # Replace with your DB name

# 2. Create a cursor object
cursor = conn.cursor()

# 3. Define the SQL statement
create_table_query = """
CREATE TABLE IF NOT EXISTS company_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    company_logo TEXT,
    product_images TEXT,
    product_description TEXT,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
"""

# 4. Execute the SQL query
cursor.execute(create_table_query)

# 5. Commit changes and close the connection
conn.commit()
conn.close()

print("Table 'company_profiles' created successfully.")
