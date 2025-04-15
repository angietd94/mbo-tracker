"""
Migration script to add email_notifications column to users table
"""
from sqlalchemy import create_engine
import os

# Get database URL from environment or use a default
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:Postgres@database-mbo-project-solutions-engineers.cluster-cnpur7nyk8zh.eu-west-3.rds.amazonaws.com/postgres')

def run_migration():
    """Run the migration to add email_notifications column to users table"""
    # Create engine and connect to the database
    engine = create_engine(DATABASE_URL)
    
    # Create a connection
    with engine.connect() as connection:
        # Begin a transaction
        with connection.begin():
            # Check if the column already exists
            result = connection.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='email_notifications'
            """)
            
            # If column doesn't exist, add it
            if result.rowcount == 0:
                print("Adding email_notifications column to users table...")
                connection.execute("""
                    ALTER TABLE users 
                    ADD COLUMN email_notifications BOOLEAN DEFAULT TRUE
                """)
                print("Migration completed successfully!")
            else:
                print("Column email_notifications already exists. Skipping migration.")

if __name__ == "__main__":
    run_migration()