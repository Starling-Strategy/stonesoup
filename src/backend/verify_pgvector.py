#!/usr/bin/env python3
"""
STONESOUP pgvector Verification Script

This script verifies that PostgreSQL with pgvector extension is properly set up
and working for the STONESOUP project. It tests vector operations, similarity
search, and HNSW indexing capabilities.
"""

import os
import sys
import asyncio
import logging
from typing import List, Optional
from dotenv import load_dotenv
import asyncpg
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class PgvectorVerifier:
    """Class to verify pgvector functionality"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.embedding_dim = int(os.getenv('EMBEDDING_DIMENSION', 1536))
        
        if not self.db_url:
            logger.error("DATABASE_URL not found in environment variables")
            sys.exit(1)
    
    async def connect(self) -> asyncpg.Connection:
        """Connect to PostgreSQL database"""
        try:
            conn = await asyncpg.connect(self.db_url)
            logger.info("✓ Successfully connected to PostgreSQL")
            return conn
        except Exception as e:
            logger.error(f"✗ Failed to connect to PostgreSQL: {e}")
            sys.exit(1)
    
    async def check_pgvector_extension(self, conn: asyncpg.Connection) -> bool:
        """Check if pgvector extension is installed"""
        try:
            result = await conn.fetchrow(
                "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'"
            )
            
            if result:
                logger.info(f"✓ pgvector extension found - version: {result['extversion']}")
                return True
            else:
                logger.error("✗ pgvector extension not found")
                return False
        except Exception as e:
            logger.error(f"✗ Error checking pgvector extension: {e}")
            return False
    
    async def test_vector_operations(self, conn: asyncpg.Connection) -> bool:
        """Test basic vector operations"""
        try:
            # Create test table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS test_vectors (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    embedding vector(3)
                )
            """)
            
            # Insert test vectors
            test_vectors = [
                ("vector1", [1.0, 2.0, 3.0]),
                ("vector2", [4.0, 5.0, 6.0]),
                ("vector3", [7.0, 8.0, 9.0]),
                ("vector4", [1.1, 2.1, 3.1]),
            ]
            
            for name, vec in test_vectors:
                await conn.execute(
                    "INSERT INTO test_vectors (name, embedding) VALUES ($1, $2)",
                    name, vec
                )
            
            logger.info("✓ Successfully inserted test vectors")
            
            # Test similarity search using cosine distance
            query_vector = [1.0, 2.0, 3.0]
            results = await conn.fetch("""
                SELECT name, embedding, 
                       embedding <-> $1::vector as cosine_distance,
                       embedding <#> $1::vector as neg_inner_product,
                       embedding <=> $1::vector as l2_distance
                FROM test_vectors
                ORDER BY embedding <-> $1::vector
                LIMIT 3
            """, query_vector)
            
            logger.info("✓ Similarity search results:")
            for row in results:
                logger.info(f"  {row['name']}: cosine_dist={row['cosine_distance']:.4f}, "
                           f"l2_dist={row['l2_distance']:.4f}")
            
            # Clean up
            await conn.execute("DROP TABLE test_vectors")
            logger.info("✓ Basic vector operations test passed")
            return True
            
        except Exception as e:
            logger.error(f"✗ Vector operations test failed: {e}")
            return False
    
    async def test_hnsw_index(self, conn: asyncpg.Connection) -> bool:
        """Test HNSW index creation and performance"""
        try:
            # Create test table with higher dimensional vectors
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS test_hnsw (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector({self.embedding_dim})
                )
            """)
            
            # Generate random test data
            np.random.seed(42)  # For reproducible results
            test_data = []
            for i in range(1000):
                # Generate random embedding
                embedding = np.random.normal(0, 1, self.embedding_dim).tolist()
                test_data.append((f"document_{i}", embedding))
            
            # Insert test data in batches
            batch_size = 100
            for i in range(0, len(test_data), batch_size):
                batch = test_data[i:i+batch_size]
                await conn.executemany(
                    "INSERT INTO test_hnsw (content, embedding) VALUES ($1, $2)",
                    batch
                )
            
            logger.info(f"✓ Inserted {len(test_data)} test vectors")
            
            # Create HNSW index
            logger.info("Creating HNSW index...")
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS test_hnsw_embedding_idx 
                ON test_hnsw USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)
            
            logger.info("✓ HNSW index created successfully")
            
            # Test query performance with and without index
            query_vector = np.random.normal(0, 1, self.embedding_dim).tolist()
            
            # Query with index
            results = await conn.fetch("""
                SELECT content, embedding <-> $1::vector as distance
                FROM test_hnsw
                ORDER BY embedding <-> $1::vector
                LIMIT 10
            """, query_vector)
            
            logger.info(f"✓ HNSW index query returned {len(results)} results")
            
            # Show query plan to verify index usage
            plan = await conn.fetchval("""
                EXPLAIN (FORMAT JSON) 
                SELECT content, embedding <-> $1::vector as distance
                FROM test_hnsw
                ORDER BY embedding <-> $1::vector
                LIMIT 10
            """, query_vector)
            
            # Check if index is being used
            plan_str = str(plan)
            if "Index Scan" in plan_str and "hnsw" in plan_str.lower():
                logger.info("✓ HNSW index is being used in query plan")
            else:
                logger.warning("⚠ HNSW index may not be used - check query plan")
            
            # Clean up
            await conn.execute("DROP TABLE test_hnsw")
            logger.info("✓ HNSW index test passed")
            return True
            
        except Exception as e:
            logger.error(f"✗ HNSW index test failed: {e}")
            return False
    
    async def test_stonesoup_schema(self, conn: asyncpg.Connection) -> bool:
        """Test STONESOUP-specific schema with cauldron_id"""
        try:
            # Create test tables that match the STONESOUP schema
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS test_cauldrons (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS test_documents (
                    id SERIAL PRIMARY KEY,
                    cauldron_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    embedding vector({self.embedding_dim}),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cauldron_id) REFERENCES test_cauldrons(id)
                )
            """)
            
            # Create HNSW index on embeddings
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS test_documents_embedding_idx 
                ON test_documents USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64)
            """)
            
            # Insert test data
            cauldron_id = await conn.fetchval("""
                INSERT INTO test_cauldrons (name, description) 
                VALUES ('Test Cauldron', 'Test cauldron for verification')
                RETURNING id
            """)
            
            # Insert test documents
            test_docs = [
                ("Document 1", "Content about machine learning"),
                ("Document 2", "Content about natural language processing"),
                ("Document 3", "Content about computer vision"),
            ]
            
            for title, content in test_docs:
                embedding = np.random.normal(0, 1, self.embedding_dim).tolist()
                await conn.execute("""
                    INSERT INTO test_documents (cauldron_id, title, content, embedding)
                    VALUES ($1, $2, $3, $4)
                """, cauldron_id, title, content, embedding)
            
            # Test similarity search within cauldron
            query_embedding = np.random.normal(0, 1, self.embedding_dim).tolist()
            results = await conn.fetch("""
                SELECT d.title, d.content, d.embedding <-> $1::vector as distance
                FROM test_documents d
                JOIN test_cauldrons c ON d.cauldron_id = c.id
                WHERE d.cauldron_id = $2
                ORDER BY d.embedding <-> $1::vector
                LIMIT 5
            """, query_embedding, cauldron_id)
            
            logger.info(f"✓ STONESOUP schema test passed - found {len(results)} documents")
            
            # Clean up
            await conn.execute("DROP TABLE test_documents")
            await conn.execute("DROP TABLE test_cauldrons")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ STONESOUP schema test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all verification tests"""
        logger.info("🧪 Starting pgvector verification tests...")
        
        conn = await self.connect()
        
        try:
            tests = [
                ("Extension Check", self.check_pgvector_extension),
                ("Vector Operations", self.test_vector_operations),
                ("HNSW Index", self.test_hnsw_index),
                ("STONESOUP Schema", self.test_stonesoup_schema),
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                logger.info(f"\n--- {test_name} ---")
                if await test_func(conn):
                    passed += 1
                    logger.info(f"✓ {test_name} passed")
                else:
                    logger.error(f"✗ {test_name} failed")
            
            logger.info(f"\n🎯 Test Results: {passed}/{total} tests passed")
            
            if passed == total:
                logger.info("🎉 All tests passed! pgvector is ready for STONESOUP")
                return True
            else:
                logger.error("❌ Some tests failed. Please check the setup.")
                return False
                
        finally:
            await conn.close()

async def main():
    """Main function"""
    print("STONESOUP pgvector Verification")
    print("=" * 40)
    
    verifier = PgvectorVerifier()
    success = await verifier.run_all_tests()
    
    if success:
        print("\n✅ Verification completed successfully!")
        print("Your PostgreSQL database with pgvector is ready for STONESOUP.")
        sys.exit(0)
    else:
        print("\n❌ Verification failed!")
        print("Please check the error messages above and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    # Check dependencies
    required_packages = ['asyncpg', 'numpy', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        sys.exit(1)
    
    asyncio.run(main())