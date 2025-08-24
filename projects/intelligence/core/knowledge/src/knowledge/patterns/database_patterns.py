"""Database and data management patterns."""

from typing import List
from ..db_manager import Pattern


def get_database_patterns() -> List[Pattern]:
    """Get database-related patterns."""
    return [
        Pattern(
            name="database_connection_pool",
            language="python",
            pattern_type="database",
            code_snippet="""
class DatabasePool:
    def __init__(self, connection_string, pool_size=10):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.connections = []
        self.available = []
        self._initialize_pool()
    
    def _initialize_pool(self):
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.connection_string)
            self.connections.append(conn)
            self.available.append(conn)
    
    def get_connection(self):
        if self.available:
            return self.available.pop()
        raise Exception("No available connections")
    
    def return_connection(self, conn):
        self.available.append(conn)
""",
            usage_context="Connection pooling for database efficiency",
            dependencies=["sqlite3"],
            success_count=28
        ),
        Pattern(
            name="database_migration_runner",
            language="python",
            pattern_type="database",
            code_snippet="""
class MigrationRunner:
    def __init__(self, db_path):
        self.db_path = db_path
        self.migrations = []
    
    def add_migration(self, version, up_sql, down_sql):
        self.migrations.append({
            'version': version,
            'up': up_sql,
            'down': down_sql
        })
    
    def migrate_up(self, target_version=None):
        conn = sqlite3.connect(self.db_path)
        current_version = self._get_current_version(conn)
        
        for migration in sorted(self.migrations, key=lambda x: x['version']):
            if migration['version'] > current_version:
                if target_version and migration['version'] > target_version:
                    break
                conn.execute(migration['up'])
                self._update_version(conn, migration['version'])
        
        conn.commit()
        conn.close()
""",
            usage_context="Database schema migration management",
            dependencies=["sqlite3"],
            success_count=22
        ),
        Pattern(
            name="database_transaction_context",
            language="python",
            pattern_type="database",
            code_snippet="""
@contextmanager
def database_transaction(connection):
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
""",
            usage_context="Safe database transaction handling",
            dependencies=["contextlib"],
            success_count=35
        ),
        Pattern(
            name="orm_base_model",
            language="python",
            pattern_type="database",
            code_snippet="""
class BaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def save(self, db):
        if hasattr(self, 'id') and self.id:
            self._update(db)
        else:
            self._insert(db)
    
    def _insert(self, db):
        fields = [k for k in self.__dict__.keys() if k != 'id']
        values = [getattr(self, f) for f in fields]
        placeholders = ','.join(['?' for _ in fields])
        
        sql = f"INSERT INTO {self.__class__.__name__.lower()} ({','.join(fields)}) VALUES ({placeholders})"
        cursor = db.execute(sql, values)
        self.id = cursor.lastrowid
    
    def _update(self, db):
        fields = [k for k in self.__dict__.keys() if k != 'id']
        set_clause = ','.join([f"{f} = ?" for f in fields])
        values = [getattr(self, f) for f in fields] + [self.id]
        
        sql = f"UPDATE {self.__class__.__name__.lower()} SET {set_clause} WHERE id = ?"
        db.execute(sql, values)
""",
            usage_context="Simple ORM base model implementation",
            dependencies=["sqlite3"],
            success_count=18
        ),
        Pattern(
            name="query_builder",
            language="python",
            pattern_type="database",
            code_snippet="""
class QueryBuilder:
    def __init__(self, table):
        self.table = table
        self.conditions = []
        self.order_by_clause = ""
        self.limit_clause = ""
    
    def where(self, condition, *args):
        self.conditions.append((condition, args))
        return self
    
    def order_by(self, column, direction="ASC"):
        self.order_by_clause = f" ORDER BY {column} {direction}"
        return self
    
    def limit(self, count):
        self.limit_clause = f" LIMIT {count}"
        return self
    
    def build(self):
        sql = f"SELECT * FROM {self.table}"
        params = []
        
        if self.conditions:
            where_parts = []
            for condition, args in self.conditions:
                where_parts.append(condition)
                params.extend(args)
            sql += " WHERE " + " AND ".join(where_parts)
        
        sql += self.order_by_clause + self.limit_clause
        return sql, params
""",
            usage_context="Fluent query building interface",
            dependencies=[],
            success_count=25
        )
    ]