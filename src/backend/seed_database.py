#!/usr/bin/env python3
"""
STONESOUP Database Seeding Script

This script populates the STONESOUP database with realistic sample data for
development and demonstration purposes. It creates a comprehensive dataset
showcasing the platform's capabilities for the Goldman Sachs 10,000 Small
Businesses program.

What This Script Does:
=====================

1. Creates a sample cauldron (organization/workspace)
2. Generates 15 diverse member profiles representing different industries
3. Creates 3-5 stories per member (60+ total stories)
4. Generates AI embeddings for semantic search capabilities
5. Establishes realistic relationships between members and stories
6. Includes metadata for testing search and filtering features

Educational Information:
=======================

About Embeddings:
----------------
Embeddings are numerical representations of text that capture semantic meaning.
They enable "smart search" that finds content based on meaning rather than
just keyword matching. For example:

- Search for "restaurant management" finds stories about "food service operations"
- Search for "customer service" finds stories about "client relations"
- Search for "leadership" finds stories about "team building" and "management"

This makes the search experience much more intuitive and powerful for users.

About the Data:
--------------
The sample data focuses on small business owners and entrepreneurs who would
benefit from Goldman Sachs 10KSB programs:

- Restaurant owners navigating growth challenges
- Tech entrepreneurs building scalable solutions
- Manufacturers implementing sustainable practices
- Service providers expanding their market reach
- Non-profit leaders driving community impact

Each profile includes realistic challenges, achievements, and expertise that
demonstrate the platform's value for business networking and knowledge sharing.

Requirements:
============
- PostgreSQL database with pgvector extension
- OpenRouter API key for embedding generation
- All required Python packages installed

Usage:
======
python seed_database.py [options]

Options:
  --clear-existing    Remove existing data before seeding
  --skip-embeddings   Skip embedding generation (faster, but no semantic search)
  --cauldron-name     Name for the sample cauldron (default: "10KSB Demo")
  --verbose          Enable verbose logging
  --help             Show this help message

Environment Variables:
=====================
- OPENROUTER_API_KEY: Required for embedding generation
- DATABASE_URL: Database connection string (optional, uses config default)

Example:
========
# Full seeding with embeddings
python seed_database.py --clear-existing --verbose

# Quick seeding without embeddings (for development)
python seed_database.py --skip-embeddings --verbose
"""

import asyncio
import argparse
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import uuid

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import STONESOUP components
from app.db.session import get_db_context, init_db
from app.models.cauldron import Cauldron
from app.models.member import Member
from app.models.story import Story, story_members, StoryStatus
from app.core.config import settings
from sqlalchemy import text

# Import seed data components
from seed_data.sample_members import generate_member_profiles
from seed_data.sample_stories import get_all_sample_stories
from seed_data.embedding_generator import EmbeddingGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('seed_database.log')
    ]
)
logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """
    Main class for seeding the STONESOUP database with sample data.
    
    This class orchestrates the entire seeding process:
    1. Database initialization and cleanup
    2. Cauldron creation
    3. Member profile generation with embeddings
    4. Story creation with embeddings
    5. Relationship establishment
    6. Data validation and reporting
    """
    
    def __init__(self, 
                 cauldron_name: str = "10KSB Demo",
                 skip_embeddings: bool = False,
                 clear_existing: bool = False,
                 verbose: bool = False):
        """
        Initialize the database seeder.
        
        Args:
            cauldron_name: Name for the sample cauldron
            skip_embeddings: Skip embedding generation for speed
            clear_existing: Remove existing data before seeding
            verbose: Enable verbose logging
        """
        self.cauldron_name = cauldron_name
        self.skip_embeddings = skip_embeddings
        self.clear_existing = clear_existing
        self.verbose = verbose
        
        # Set logging level
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Initialize embedding generator
        self.embedding_generator = None
        if not skip_embeddings:
            self.embedding_generator = EmbeddingGenerator(
                cache_dir="./embedding_cache"
            )
        
        # Track seeding statistics
        self.stats = {
            "start_time": None,
            "end_time": None,
            "cauldrons_created": 0,
            "members_created": 0,
            "stories_created": 0,
            "embeddings_generated": 0,
            "relationships_created": 0,
            "errors": []
        }
    
    async def validate_environment(self) -> bool:
        """
        Validate that the environment is properly configured.
        
        Returns:
            True if environment is valid, False otherwise
        """
        logger.info("Validating environment...")
        
        # Check database connection
        try:
            async with get_db_context() as db:
                # Test basic query
                result = await db.execute(text("SELECT 1"))
                logger.info("✓ Database connection successful")
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            return False
        
        # Check OpenRouter API key if embeddings are enabled
        if not self.skip_embeddings:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                logger.error("✗ OPENROUTER_API_KEY environment variable not set")
                logger.error("  Either set the API key or use --skip-embeddings")
                return False
            logger.info("✓ OpenRouter API key found")
        
        # Check pgvector extension
        try:
            async with get_db_context() as db:
                result = await db.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'"))
                if result.fetchone():
                    logger.info("✓ pgvector extension installed")
                else:
                    logger.error("✗ pgvector extension not installed")
                    logger.error("  Run: CREATE EXTENSION vector;")
                    return False
        except Exception as e:
            logger.error(f"✗ Failed to check pgvector extension: {e}")
            return False
        
        logger.info("Environment validation successful")
        return True
    
    async def clear_existing_data(self) -> None:
        """
        Clear existing seed data from the database.
        
        This removes all data from the demo cauldron to ensure a clean seed.
        """
        logger.info("Clearing existing data...")
        
        async with get_db_context() as db:
            # Find existing demo cauldron
            existing_cauldron = await db.execute(
                "SELECT id FROM cauldrons WHERE name = :name",
                {"name": self.cauldron_name}
            )
            cauldron_row = existing_cauldron.fetchone()
            
            if cauldron_row:
                cauldron_id = cauldron_row[0]
                logger.info(f"Found existing cauldron: {cauldron_id}")
                
                # Delete in correct order due to foreign key constraints
                # 1. Story-member relationships
                await db.execute(
                    "DELETE FROM story_members WHERE cauldron_id = :cauldron_id",
                    {"cauldron_id": cauldron_id}
                )
                
                # 2. Stories
                result = await db.execute(
                    "DELETE FROM stories WHERE cauldron_id = :cauldron_id",
                    {"cauldron_id": cauldron_id}
                )
                logger.info(f"Deleted {result.rowcount} stories")
                
                # 3. Members
                result = await db.execute(
                    "DELETE FROM members WHERE cauldron_id = :cauldron_id",
                    {"cauldron_id": cauldron_id}
                )
                logger.info(f"Deleted {result.rowcount} members")
                
                # 4. Cauldron
                await db.execute(
                    "DELETE FROM cauldrons WHERE id = :cauldron_id",
                    {"cauldron_id": cauldron_id}
                )
                logger.info("Deleted cauldron")
        
        logger.info("Existing data cleared")
    
    async def create_sample_cauldron(self) -> str:
        """
        Create a sample cauldron for the seed data.
        
        Returns:
            UUID of the created cauldron
        """
        logger.info(f"Creating sample cauldron: {self.cauldron_name}")
        
        # Create cauldron data
        cauldron_data = {
            "name": self.cauldron_name,
            "slug": self.cauldron_name.lower().replace(" ", "-"),
            "description": """
            A demonstration workspace for Goldman Sachs 10,000 Small Businesses program participants.
            
            This cauldron showcases the STONESOUP platform's capabilities for connecting entrepreneurs,
            sharing success stories, and building a community of business leaders committed to growth
            and mutual support.
            
            Features demonstrated:
            - Diverse member profiles across industries
            - Rich storytelling with achievements and case studies
            - Semantic search powered by AI embeddings
            - Skill-based matching and recommendations
            - Community-driven knowledge sharing
            """.strip(),
            "global_guidance_prompt": """
            You are assisting members of the Goldman Sachs 10,000 Small Businesses program.
            Focus on practical business advice, growth strategies, and community building.
            Encourage collaboration, knowledge sharing, and mutual support among entrepreneurs.
            
            When generating content or providing guidance:
            1. Emphasize actionable business insights
            2. Highlight the value of peer learning
            3. Connect members with complementary skills
            4. Promote diversity and inclusion
            5. Support sustainable business practices
            """.strip(),
            "embedding_model": "openai/text-embedding-3-small",
            "features": {
                "story_generation": True,
                "ai_matching": True,
                "semantic_search": True,
                "skill_recommendations": True,
                "community_features": True
            },
            "logo_url": "https://stonesoup.ai/logos/10ksb-demo.png",
            "primary_color": "#1F2937",  # Professional dark blue
            "is_active": True,
            "is_public": True,
            "subscription_tier": "enterprise",
            "member_limit": {"max": 500, "current": 0},
            "story_limit": {"max": 5000, "current": 0},
            "owner_id": str(uuid.uuid4()),  # Demo owner
            "extra_metadata": {
                "demo_cauldron": True,
                "program": "Goldman Sachs 10KSB",
                "purpose": "Demonstration and development",
                "seed_version": "1.0.0",
                "created_by": "STONESOUP Seed Script"
            }
        }
        
        # Create cauldron in database
        async with get_db_context() as db:
            cauldron = Cauldron(**cauldron_data)
            db.add(cauldron)
            await db.flush()  # Get the ID
            
            cauldron_id = str(cauldron.id)
            self.stats["cauldrons_created"] += 1
            
            logger.info(f"Created cauldron: {cauldron_id}")
            return cauldron_id
    
    async def create_members_with_embeddings(self, cauldron_id: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Create member profiles with embeddings.
        
        Args:
            cauldron_id: UUID of the cauldron
            
        Returns:
            List of (member_id, member_data) tuples
        """
        logger.info("Creating member profiles...")
        
        # Generate member profiles
        member_profiles = generate_member_profiles()
        logger.info(f"Generated {len(member_profiles)} member profiles")
        
        # Generate embeddings if not skipping
        if not self.skip_embeddings:
            logger.info("Generating embeddings for member profiles...")
            member_embeddings = await self.embedding_generator.generate_member_embeddings(member_profiles)
            self.stats["embeddings_generated"] += len(member_embeddings)
        else:
            member_embeddings = [(member, None) for member in member_profiles]
        
        # Create members in database
        created_members = []
        async with get_db_context() as db:
            for member_data, embedding in member_embeddings:
                try:
                    # Prepare member data for database
                    member_db_data = {
                        **member_data,
                        "cauldron_id": cauldron_id,
                        "profile_embedding": embedding
                    }
                    
                    # Create member
                    member = Member(**member_db_data)
                    db.add(member)
                    await db.flush()
                    
                    created_members.append((str(member.id), member_data))
                    self.stats["members_created"] += 1
                    
                    logger.debug(f"Created member: {member_data['name']}")
                    
                except Exception as e:
                    logger.error(f"Failed to create member {member_data.get('name', 'Unknown')}: {e}")
                    self.stats["errors"].append(f"Member creation: {e}")
        
        logger.info(f"Created {len(created_members)} members")
        return created_members
    
    async def create_stories_with_embeddings(self, cauldron_id: str, members: List[Tuple[str, Dict[str, Any]]]) -> List[str]:
        """
        Create stories with embeddings and member relationships.
        
        Args:
            cauldron_id: UUID of the cauldron
            members: List of (member_id, member_data) tuples
            
        Returns:
            List of created story IDs
        """
        logger.info("Creating stories...")
        
        # Generate stories for all members
        all_stories = get_all_sample_stories(cauldron_id)
        logger.info(f"Generated {len(all_stories)} stories")
        
        # Generate embeddings if not skipping
        if not self.skip_embeddings:
            logger.info("Generating embeddings for stories...")
            story_embeddings = await self.embedding_generator.generate_story_embeddings(all_stories)
            self.stats["embeddings_generated"] += len(story_embeddings)
        else:
            story_embeddings = [(story, None) for story in all_stories]
        
        # Create member email to ID mapping
        member_email_to_id = {member_data["email"]: member_id for member_id, member_data in members}
        
        # Create stories in database
        created_story_ids = []
        async with get_db_context() as db:
            for story_data, embedding in story_embeddings:
                try:
                    # Prepare story data for database
                    story_db_data = {
                        **story_data,
                        "cauldron_id": cauldron_id,
                        "embedding": embedding,
                        "status": StoryStatus.PUBLISHED,
                        "published_at": story_data.get("occurred_at")
                    }
                    
                    # Create story
                    story = Story(**story_db_data)
                    db.add(story)
                    await db.flush()
                    
                    story_id = str(story.id)
                    created_story_ids.append(story_id)
                    self.stats["stories_created"] += 1
                    
                    # Find the member who authored this story
                    author_member_id = None
                    for member_id, member_data in members:
                        if story_data.get("company") == member_data.get("company"):
                            author_member_id = member_id
                            break
                    
                    # Create story-member relationship
                    if author_member_id:
                        await db.execute(
                            """
                            INSERT INTO story_members (story_id, member_id, cauldron_id, role, created_at)
                            VALUES (:story_id, :member_id, :cauldron_id, :role, :created_at)
                            """,
                            {
                                "story_id": story_id,
                                "member_id": author_member_id,
                                "cauldron_id": cauldron_id,
                                "role": "author",
                                "created_at": datetime.utcnow()
                            }
                        )
                        self.stats["relationships_created"] += 1
                    
                    logger.debug(f"Created story: {story_data['title'][:50]}...")
                    
                except Exception as e:
                    logger.error(f"Failed to create story {story_data.get('title', 'Unknown')}: {e}")
                    self.stats["errors"].append(f"Story creation: {e}")
        
        logger.info(f"Created {len(created_story_ids)} stories")
        return created_story_ids
    
    async def update_cauldron_counts(self, cauldron_id: str) -> None:
        """
        Update the cauldron's member and story counts.
        
        Args:
            cauldron_id: UUID of the cauldron
        """
        logger.info("Updating cauldron counts...")
        
        async with get_db_context() as db:
            # Count members
            member_count = await db.execute(
                "SELECT COUNT(*) FROM members WHERE cauldron_id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            member_count = member_count.fetchone()[0]
            
            # Count stories
            story_count = await db.execute(
                "SELECT COUNT(*) FROM stories WHERE cauldron_id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            story_count = story_count.fetchone()[0]
            
            # Update cauldron
            await db.execute(
                """
                UPDATE cauldrons 
                SET member_limit = :member_limit, story_limit = :story_limit
                WHERE id = :cauldron_id
                """,
                {
                    "cauldron_id": cauldron_id,
                    "member_limit": {"max": 500, "current": member_count},
                    "story_limit": {"max": 5000, "current": story_count}
                }
            )
            
            logger.info(f"Updated cauldron counts: {member_count} members, {story_count} stories")
    
    async def validate_seed_data(self, cauldron_id: str) -> bool:
        """
        Validate the seeded data for consistency and correctness.
        
        Args:
            cauldron_id: UUID of the cauldron
            
        Returns:
            True if validation passes, False otherwise
        """
        logger.info("Validating seed data...")
        
        validation_errors = []
        
        async with get_db_context() as db:
            # Check cauldron exists
            cauldron = await db.execute(
                "SELECT id, name FROM cauldrons WHERE id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            if not cauldron.fetchone():
                validation_errors.append("Cauldron not found")
            
            # Check members exist
            member_count = await db.execute(
                "SELECT COUNT(*) FROM members WHERE cauldron_id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            member_count = member_count.fetchone()[0]
            if member_count == 0:
                validation_errors.append("No members found")
            
            # Check stories exist
            story_count = await db.execute(
                "SELECT COUNT(*) FROM stories WHERE cauldron_id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            story_count = story_count.fetchone()[0]
            if story_count == 0:
                validation_errors.append("No stories found")
            
            # Check relationships exist
            relationship_count = await db.execute(
                "SELECT COUNT(*) FROM story_members WHERE cauldron_id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            relationship_count = relationship_count.fetchone()[0]
            if relationship_count == 0:
                validation_errors.append("No story-member relationships found")
            
            # Check embeddings if not skipped
            if not self.skip_embeddings:
                member_embeddings = await db.execute(
                    "SELECT COUNT(*) FROM members WHERE cauldron_id = :cauldron_id AND profile_embedding IS NOT NULL",
                    {"cauldron_id": cauldron_id}
                )
                member_embeddings = member_embeddings.fetchone()[0]
                if member_embeddings == 0:
                    validation_errors.append("No member embeddings found")
                
                story_embeddings = await db.execute(
                    "SELECT COUNT(*) FROM stories WHERE cauldron_id = :cauldron_id AND embedding IS NOT NULL",
                    {"cauldron_id": cauldron_id}
                )
                story_embeddings = story_embeddings.fetchone()[0]
                if story_embeddings == 0:
                    validation_errors.append("No story embeddings found")
        
        if validation_errors:
            logger.error("Validation failed:")
            for error in validation_errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("Validation successful")
        return True
    
    async def generate_summary_report(self, cauldron_id: str) -> Dict[str, Any]:
        """
        Generate a summary report of the seeded data.
        
        Args:
            cauldron_id: UUID of the cauldron
            
        Returns:
            Dictionary containing summary statistics
        """
        logger.info("Generating summary report...")
        
        async with get_db_context() as db:
            # Get cauldron info
            cauldron = await db.execute(
                "SELECT name, slug, description FROM cauldrons WHERE id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            cauldron_info = cauldron.fetchone()
            
            # Get member statistics
            member_stats = await db.execute(
                """
                SELECT 
                    COUNT(*) as total_members,
                    COUNT(DISTINCT company) as unique_companies,
                    AVG(years_of_experience) as avg_experience,
                    COUNT(CASE WHEN profile_embedding IS NOT NULL THEN 1 END) as members_with_embeddings
                FROM members 
                WHERE cauldron_id = :cauldron_id
                """,
                {"cauldron_id": cauldron_id}
            )
            member_stats = member_stats.fetchone()
            
            # Get story statistics
            story_stats = await db.execute(
                """
                SELECT 
                    COUNT(*) as total_stories,
                    COUNT(DISTINCT story_type) as unique_story_types,
                    COUNT(DISTINCT company) as unique_companies,
                    COUNT(CASE WHEN embedding IS NOT NULL THEN 1 END) as stories_with_embeddings
                FROM stories 
                WHERE cauldron_id = :cauldron_id
                """,
                {"cauldron_id": cauldron_id}
            )
            story_stats = story_stats.fetchone()
            
            # Get industry breakdown
            industry_stats = await db.execute(
                """
                SELECT 
                    jsonb_array_elements_text(industries) as industry,
                    COUNT(*) as member_count
                FROM members 
                WHERE cauldron_id = :cauldron_id
                GROUP BY industry
                ORDER BY member_count DESC
                """,
                {"cauldron_id": cauldron_id}
            )
            industries = industry_stats.fetchall()
            
            # Get embedding statistics
            embedding_stats = {}
            if self.embedding_generator:
                embedding_stats = self.embedding_generator.get_stats()
        
        # Compile report
        report = {
            "cauldron": {
                "id": cauldron_id,
                "name": cauldron_info[0] if cauldron_info else "Unknown",
                "slug": cauldron_info[1] if cauldron_info else "unknown",
            },
            "members": {
                "total": member_stats[0] if member_stats else 0,
                "unique_companies": member_stats[1] if member_stats else 0,
                "avg_experience_years": round(member_stats[2] or 0, 1),
                "with_embeddings": member_stats[3] if member_stats else 0,
            },
            "stories": {
                "total": story_stats[0] if story_stats else 0,
                "unique_types": story_stats[1] if story_stats else 0,
                "unique_companies": story_stats[2] if story_stats else 0,
                "with_embeddings": story_stats[3] if story_stats else 0,
            },
            "industries": [
                {"industry": industry[0], "member_count": industry[1]}
                for industry in industries
            ],
            "seeding_stats": self.stats,
            "embedding_stats": embedding_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return report
    
    async def run_seed(self) -> bool:
        """
        Execute the complete seeding process.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.stats["start_time"] = datetime.utcnow()
            
            logger.info("=" * 60)
            logger.info("STONESOUP Database Seeding Started")
            logger.info("=" * 60)
            
            # 1. Validate environment
            if not await self.validate_environment():
                return False
            
            # 2. Initialize database
            logger.info("Initializing database...")
            await init_db()
            
            # 3. Clear existing data if requested
            if self.clear_existing:
                await self.clear_existing_data()
            
            # 4. Create sample cauldron
            cauldron_id = await self.create_sample_cauldron()
            
            # 5. Create members with embeddings
            members = await self.create_members_with_embeddings(cauldron_id)
            
            # 6. Create stories with embeddings
            stories = await self.create_stories_with_embeddings(cauldron_id, members)
            
            # 7. Update cauldron counts
            await self.update_cauldron_counts(cauldron_id)
            
            # 8. Validate seed data
            if not await self.validate_seed_data(cauldron_id):
                return False
            
            # 9. Generate summary report
            report = await self.generate_summary_report(cauldron_id)
            
            # 10. Success summary
            self.stats["end_time"] = datetime.utcnow()
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
            
            logger.info("=" * 60)
            logger.info("STONESOUP Database Seeding Completed Successfully!")
            logger.info("=" * 60)
            logger.info(f"Duration: {duration:.1f} seconds")
            logger.info(f"Cauldron: {report['cauldron']['name']} ({cauldron_id})")
            logger.info(f"Members: {report['members']['total']} created")
            logger.info(f"Stories: {report['stories']['total']} created")
            logger.info(f"Relationships: {self.stats['relationships_created']} created")
            logger.info(f"Embeddings: {self.stats['embeddings_generated']} generated")
            
            if self.stats["errors"]:
                logger.warning(f"Errors encountered: {len(self.stats['errors'])}")
                for error in self.stats["errors"]:
                    logger.warning(f"  - {error}")
            
            # Save detailed report
            report_file = f"seed_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                import json
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Detailed report saved to: {report_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            self.stats["errors"].append(f"Fatal error: {e}")
            return False


def main():
    """Main entry point for the seeding script."""
    parser = argparse.ArgumentParser(
        description="Seed the STONESOUP database with sample data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--clear-existing",
        action="store_true",
        help="Remove existing data before seeding"
    )
    
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Skip embedding generation (faster, but no semantic search)"
    )
    
    parser.add_argument(
        "--cauldron-name",
        default="10KSB Demo",
        help="Name for the sample cauldron"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Create seeder
    seeder = DatabaseSeeder(
        cauldron_name=args.cauldron_name,
        skip_embeddings=args.skip_embeddings,
        clear_existing=args.clear_existing,
        verbose=args.verbose
    )
    
    # Run seeding
    success = asyncio.run(seeder.run_seed())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()