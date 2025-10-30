from src.dao.db_connection import DBConnection

def init_db(dsn):
    with DBConnection(dsn) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CONVERSATIONS (
                id SERIAL PRIMARY KEY,
                titre TEXT NOT NULL,
                date_creation TIMESTAMP DEFAULT NOW(),
                owner_id INTEGER NOT NULL
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS MESSAGES (
            id SERIAL PRIMARY KEY ,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id),
            sender_type, 
            content TEXT
            created_at TIMESTAMP DEfAULT NOW()
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CONVERSATIONS_PARTICIPANTS (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id))
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS USERS (
            idSERIAL PRIMARY KEY,
            username TEXT,
            password_hash TEXT)
        """)
    
    
    
    
    print("✅ Table 'CONVERSATIONS', 'MESSAGES', 'CONVERSATIONS_PARTICIPANTS', 'USERS' vérifiée ou créée.")





if __name__ == "__main__":
    dsn = "dbname=test user=postgres password=secret host=localhost"
    init_db(dsn)