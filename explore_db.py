#!/usr/bin/env python3
"""
Database exploration script for the murmuration schema.
This script connects to the PostgreSQL database and explores the schema structure.
"""

import os
import psycopg2
from psycopg2 import sql
from tabulate import tabulate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection():
    """Create a database connection using the DATABASE_URL from .env"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    return psycopg2.connect(database_url)

def list_schemas(conn):
    """List all schemas in the database"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schema_name;
        """)
        schemas = cur.fetchall()
        print("\n=== Database Schemas ===")
        for schema in schemas:
            print(f"  - {schema[0]}")
        return [s[0] for s in schemas]

def list_tables_in_schema(conn, schema_name='murmuration'):
    """List all tables in the specified schema"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
            ORDER BY table_name;
        """, (schema_name,))
        tables = cur.fetchall()
        print(f"\n=== Tables in '{schema_name}' schema ===")
        for table in tables:
            print(f"  - {table[0]}")
        return [t[0] for t in tables]

def describe_table(conn, schema_name, table_name):
    """Get the structure of a specific table"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema_name, table_name))
        columns = cur.fetchall()
        
        print(f"\n=== Structure of {schema_name}.{table_name} ===")
        headers = ['Column', 'Type', 'Max Length', 'Nullable', 'Default']
        print(tabulate(columns, headers=headers, tablefmt='grid'))
        
        # Get indexes
        cur.execute("""
            SELECT 
                i.relname as index_name,
                array_to_string(array_agg(a.attname), ', ') as columns
            FROM pg_class t,
                 pg_class i,
                 pg_index ix,
                 pg_attribute a,
                 pg_namespace n
            WHERE t.oid = ix.indrelid
                AND i.oid = ix.indexrelid
                AND a.attrelid = t.oid
                AND a.attnum = ANY(ix.indkey)
                AND t.relkind = 'r'
                AND n.oid = t.relnamespace
                AND n.nspname = %s
                AND t.relname = %s
            GROUP BY i.relname
            ORDER BY i.relname;
        """, (schema_name, table_name))
        indexes = cur.fetchall()
        
        if indexes:
            print(f"\n  Indexes:")
            for idx in indexes:
                print(f"    - {idx[0]}: ({idx[1]})")

def count_records(conn, schema_name, table_name):
    """Count records in a table"""
    with conn.cursor() as cur:
        query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name)
        )
        cur.execute(query)
        count = cur.fetchone()[0]
        return count

def get_sample_data(conn, schema_name, table_name, limit=5):
    """Get sample records from a table"""
    with conn.cursor() as cur:
        # Get column names
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema_name, table_name))
        columns = [col[0] for col in cur.fetchall()]
        
        # Get sample data
        query = sql.SQL("SELECT * FROM {}.{} LIMIT %s").format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name)
        )
        cur.execute(query, (limit,))
        rows = cur.fetchall()
        
        if rows:
            print(f"\n=== Sample data from {schema_name}.{table_name} (first {limit} rows) ===")
            print(tabulate(rows, headers=columns, tablefmt='grid'))
        else:
            print(f"\n=== No data in {schema_name}.{table_name} ===")

def main():
    """Main exploration function"""
    try:
        print("Connecting to PostgreSQL database...")
        conn = get_connection()
        
        # List all schemas
        schemas = list_schemas(conn)
        
        # Check if murmuration schema exists
        if 'murmuration' not in schemas:
            print("\n❌ 'murmuration' schema not found!")
            print("Available schemas:", schemas)
            return
        
        # List tables in murmuration schema
        tables = list_tables_in_schema(conn, 'murmuration')
        
        if not tables:
            print("\n❌ No tables found in 'murmuration' schema!")
            return
        
        # For each table, show structure and count
        print("\n=== Table Details ===")
        table_counts = {}
        for table in tables:
            count = count_records(conn, 'murmuration', table)
            table_counts[table] = count
            print(f"\n{table}: {count} records")
            
            # Show structure for key tables
            if table in ['members', 'stories', 'skills', 'contributions']:
                describe_table(conn, 'murmuration', table)
                
                # Show sample data if table has records
                if count > 0:
                    get_sample_data(conn, 'murmuration', table)
        
        # Summary
        print("\n=== Summary ===")
        print(f"Total tables in murmuration schema: {len(tables)}")
        print("\nRecord counts:")
        for table, count in sorted(table_counts.items()):
            print(f"  - {table}: {count}")
        
        conn.close()
        print("\n✅ Database exploration complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()