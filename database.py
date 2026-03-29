import sqlite3

def init_db():
    conn = sqlite3.connect('laptops.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS selections 
                      (user_id INTEGER, category TEXT)''')
    conn.commit()
    conn.close()

def log_selection(user_id, category):
    conn = sqlite3.connect('laptops.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO selections (user_id, category) VALUES (?, ?)',
                   (user_id, category))
    conn.commit()
    conn.close()