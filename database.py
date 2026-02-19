import sqlite3

def init_db():
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            year TEXT NOT NULL,
            filename TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_note(title, content, year, filename):
    conn = sqlite3.connect("notes.db")
    c = conn.cursor()
    c.execute('INSERT INTO notes (title, content, year, filename) VALUES (?, ?, ?, ?)',
              (title, content, year, filename))
    conn.commit()
    conn.close()
