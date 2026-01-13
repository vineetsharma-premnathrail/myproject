import os, shutil, sqlite3
DB='test.db'
BACKUP='test.db.before_delete_users.bak'
if not os.path.exists(DB):
    print('No test.db found in workspace root')
else:
    try:
        shutil.copy2(DB, BACKUP)
        print('Backup created:', BACKUP)
    except Exception as e:
        print('Backup failed:', e)
    try:
        conn=sqlite3.connect(DB)
        cur=conn.cursor()
        cur.execute('PRAGMA foreign_keys = OFF;')
        cur.execute('DELETE FROM users;')
        conn.commit()
        print('All users deleted from users table')
        conn.close()
    except Exception as e:
        print('Delete failed:', e)
