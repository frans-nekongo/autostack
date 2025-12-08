
# autostack_engine/scripts/create_migration.py
import os
from pathlib import Path
from datetime import datetime
import sys

MIGRATION_TEMPLATE = '''"""
Migration: {description}
Created: {timestamp}
"""

async def up():
    """
    Apply the migration
    """
    # Add your migration logic here
    pass


async def down():
    """
    Rollback the migration
    """
    # Add your rollback logic here
    pass
'''

def create_migration(description: str):
    """Create a new migration file"""
    migrations_dir = Path("migrations")
    migrations_dir.mkdir(exist_ok=True)
    
    # Generate timestamp-based version
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Clean description for filename
    clean_description = description.lower().replace(" ", "_").replace("-", "_")
    filename = f"{timestamp}_{clean_description}.py"
    
    migration_path = migrations_dir / filename
    
    content = MIGRATION_TEMPLATE.format(
        description=description,
        timestamp=datetime.utcnow().isoformat()
    )
    
    with open(migration_path, 'w') as f:
        f.write(content)
    
    print(f"Created migration: {migration_path}")
    return migration_path

def main():
    """Main entry point for create-migration script"""
    if len(sys.argv) < 2:
        print("Usage: create-migration <description>")
        sys.exit(1)
    
    description = " ".join(sys.argv[1:])
    create_migration(description)

if __name__ == "__main__":
    main()


