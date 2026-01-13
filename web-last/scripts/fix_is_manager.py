from app.db.session import SessionLocal
from app.db import models

# Create a database session
db = SessionLocal()

try:
    # Update any NULL is_manager values to False
    updated_count = db.query(models.User).filter(models.User.is_manager.is_(None)).update({"is_manager": False})
    db.commit()

    print(f"Updated {updated_count} user records where is_manager was NULL")

except Exception as e:
    print(f"Error fixing database: {e}")
    db.rollback()

finally:
    db.close()

print("Database fix completed")