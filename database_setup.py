import sqlite3
 
conn = sqlite3.connect("database.db")
c = conn.cursor()

#Username, password, unique id, mood

# journal logs: journal entry, user id, date, content, evaluation by vader

#: motivational quotes

c.execute("""CREATE TABLE Users(
user_ID INT,
user_name TEXT,
password TEXT,
mood REAL,
PRIMARY KEY(user_ID)    
)""")
conn.commit()

c.execute("""CREATE TABLE Journal(
journal_ID INT,
user_ID INT,
content TEXT,
date TEXT,
evaluation REAL,
PRIMARY KEY(journal_ID),
FOREIGN KEY (user_ID) REFERENCES Users(user_ID)
)""")

conn.commit()

c.execute("""CREATE TABLE Quotes(
quote_ID INT,
quote TEXT,
PRIMARY KEY(quote_ID))""")

conn.commit()
conn.close()