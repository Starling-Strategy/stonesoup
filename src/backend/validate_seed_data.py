#!/usr/bin/env python3
"""
STONESOUP Seed Data Validation Script

This script validates the seeded data to ensure everything was created correctly
and the semantic search capabilities are working as expected.

Usage:
    python validate_seed_data.py [--cauldron-name "10KSB Demo"]
"""

import asyncio
import argparse
import sys
import os
from typing import List, Dict, Any, Tuple
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import get_db_context
from app.ai.openrouter_client import OpenRouterClient
import numpy as np


async def validate_database_data(cauldron_name: str = "10KSB Demo") -> Dict[str, Any]:
    """Validate basic database data integrity."""
    
    results = {
        "database_validation": {
            "cauldron_found": False,
            "member_count": 0,
            "story_count": 0,
            "relationship_count": 0,
            "members_with_embeddings": 0,
            "stories_with_embeddings": 0,
            "issues": []
        }
    }
    
    try:
        async with get_db_context() as db:
            # Find cauldron
            cauldron_result = await db.execute(
                "SELECT id, name, member_limit, story_limit FROM cauldrons WHERE name = :name",
                {"name": cauldron_name}
            )
            cauldron = cauldron_result.fetchone()
            
            if not cauldron:
                results["database_validation"]["issues"].append(f"Cauldron '{cauldron_name}' not found")
                return results
            
            cauldron_id = cauldron[0]
            results["database_validation"]["cauldron_found"] = True
            results["database_validation"]["cauldron_id"] = str(cauldron_id)
            
            # Count members
            member_result = await db.execute(
                "SELECT COUNT(*) FROM members WHERE cauldron_id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            member_count = member_result.fetchone()[0]
            results["database_validation"]["member_count"] = member_count
            
            # Count stories
            story_result = await db.execute(
                "SELECT COUNT(*) FROM stories WHERE cauldron_id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            story_count = story_result.fetchone()[0]
            results["database_validation"]["story_count"] = story_count
            
            # Count relationships
            rel_result = await db.execute(
                "SELECT COUNT(*) FROM story_members WHERE cauldron_id = :cauldron_id",
                {"cauldron_id": cauldron_id}
            )
            relationship_count = rel_result.fetchone()[0]
            results["database_validation"]["relationship_count"] = relationship_count
            
            # Count embeddings
            member_embed_result = await db.execute(
                "SELECT COUNT(*) FROM members WHERE cauldron_id = :cauldron_id AND profile_embedding IS NOT NULL",
                {"cauldron_id": cauldron_id}
            )
            members_with_embeddings = member_embed_result.fetchone()[0]
            results["database_validation"]["members_with_embeddings"] = members_with_embeddings
            
            story_embed_result = await db.execute(
                "SELECT COUNT(*) FROM stories WHERE cauldron_id = :cauldron_id AND embedding IS NOT NULL",
                {"cauldron_id": cauldron_id}
            )
            stories_with_embeddings = story_embed_result.fetchone()[0]
            results["database_validation"]["stories_with_embeddings"] = stories_with_embeddings
            
            # Validation checks
            if member_count == 0:
                results["database_validation"]["issues"].append("No members found")
            elif member_count < 10:
                results["database_validation"]["issues"].append(f"Low member count: {member_count}")
            
            if story_count == 0:
                results["database_validation"]["issues"].append("No stories found")
            elif story_count < 30:
                results["database_validation"]["issues"].append(f"Low story count: {story_count}")
            
            if relationship_count == 0:
                results["database_validation"]["issues"].append("No story-member relationships found")
            
            if members_with_embeddings < member_count:
                missing = member_count - members_with_embeddings
                results["database_validation"]["issues"].append(f"{missing} members missing embeddings")
            
            if stories_with_embeddings < story_count:
                missing = story_count - stories_with_embeddings
                results["database_validation"]["issues"].append(f"{missing} stories missing embeddings")
    
    except Exception as e:
        results["database_validation"]["issues"].append(f"Database error: {str(e)}")
    
    return results


async def test_semantic_search(cauldron_name: str = "10KSB Demo") -> Dict[str, Any]:
    """Test semantic search functionality."""
    
    results = {
        "semantic_search": {
            "test_queries": [],
            "embedding_quality": {},
            "issues": []
        }
    }
    
    # Test queries that should find relevant content
    test_queries = [
        {
            "query": "restaurant management",
            "expected_themes": ["food service", "restaurant", "culinary", "hospitality"],
            "min_results": 2
        },
        {
            "query": "technology startup",
            "expected_themes": ["tech", "software", "ai", "development"],
            "min_results": 2
        },
        {
            "query": "sustainable business practices",
            "expected_themes": ["sustainability", "environmental", "green", "eco"],
            "min_results": 1
        },
        {
            "query": "crisis management",
            "expected_themes": ["covid", "pandemic", "challenge", "pivot"],
            "min_results": 1
        },
        {
            "query": "team leadership",
            "expected_themes": ["staff", "employee", "management", "team"],
            "min_results": 2
        }
    ]
    
    try:
        # Get cauldron ID
        async with get_db_context() as db:
            cauldron_result = await db.execute(
                "SELECT id FROM cauldrons WHERE name = :name",
                {"name": cauldron_name}
            )
            cauldron = cauldron_result.fetchone()
            
            if not cauldron:
                results["semantic_search"]["issues"].append(f"Cauldron '{cauldron_name}' not found")
                return results
            
            cauldron_id = cauldron[0]
            
            # Initialize OpenRouter client for embeddings
            try:
                from app.ai.openrouter_client import OpenRouterClient, OpenRouterConfig
                config = OpenRouterConfig(embedding_model="openai/text-embedding-3-small")
                client = OpenRouterClient(config)
            except Exception as e:
                results["semantic_search"]["issues"].append(f"Could not initialize embedding client: {str(e)}")
                return results
            
            # Test each query
            for test_query in test_queries:
                query_results = {
                    "query": test_query["query"],
                    "results_found": 0,
                    "top_matches": [],
                    "themes_found": [],
                    "passed": False
                }
                
                try:
                    # Generate embedding for query
                    query_embedding = await client.generate_embedding(test_query["query"])
                    
                    # Search for similar stories
                    search_result = await db.execute(
                        """
                        SELECT 
                            s.title,
                            s.content,
                            s.tags,
                            s.company,
                            (s.embedding <=> :query_embedding::vector) as similarity
                        FROM stories s
                        WHERE s.cauldron_id = :cauldron_id 
                        AND s.embedding IS NOT NULL
                        ORDER BY similarity
                        LIMIT 5
                        """,
                        {
                            "cauldron_id": cauldron_id,
                            "query_embedding": query_embedding
                        }
                    )
                    
                    matches = search_result.fetchall()
                    query_results["results_found"] = len(matches)
                    
                    # Analyze matches
                    for match in matches:
                        title, content, tags, company, similarity = match
                        
                        # Convert similarity to percentage (lower distance = higher similarity)
                        similarity_pct = max(0, (1 - similarity) * 100)
                        
                        match_info = {
                            "title": title,
                            "company": company,
                            "similarity_percentage": round(similarity_pct, 1),
                            "tags": tags or []
                        }
                        query_results["top_matches"].append(match_info)
                        
                        # Check for expected themes
                        text_to_check = f"{title} {content}".lower()
                        for theme in test_query["expected_themes"]:
                            if theme.lower() in text_to_check and theme not in query_results["themes_found"]:
                                query_results["themes_found"].append(theme)
                    
                    # Determine if test passed
                    themes_found = len(query_results["themes_found"])
                    results_found = query_results["results_found"]
                    min_results = test_query["min_results"]
                    
                    query_results["passed"] = (
                        results_found >= min_results and 
                        themes_found > 0
                    )
                    
                except Exception as e:
                    query_results["error"] = str(e)
                    results["semantic_search"]["issues"].append(f"Query '{test_query['query']}' failed: {str(e)}")
                
                results["semantic_search"]["test_queries"].append(query_results)
            
            # Overall assessment
            passed_tests = sum(1 for q in results["semantic_search"]["test_queries"] if q.get("passed", False))
            total_tests = len(test_queries)
            
            results["semantic_search"]["embedding_quality"] = {
                "tests_passed": passed_tests,
                "total_tests": total_tests,
                "pass_percentage": round((passed_tests / total_tests) * 100, 1) if total_tests > 0 else 0,
                "quality_rating": "Excellent" if passed_tests >= total_tests * 0.8 else 
                                "Good" if passed_tests >= total_tests * 0.6 else
                                "Fair" if passed_tests >= total_tests * 0.4 else "Poor"
            }
    
    except Exception as e:
        results["semantic_search"]["issues"].append(f"Semantic search test failed: {str(e)}")
    
    return results


async def check_data_diversity(cauldron_name: str = "10KSB Demo") -> Dict[str, Any]:
    """Check diversity of the seeded data."""
    
    results = {
        "data_diversity": {
            "industries": [],
            "story_types": [],
            "companies": [],
            "skills": [],
            "geographic_distribution": [],
            "diversity_score": 0,
            "issues": []
        }
    }
    
    try:
        async with get_db_context() as db:
            # Get cauldron ID
            cauldron_result = await db.execute(
                "SELECT id FROM cauldrons WHERE name = :name",
                {"name": cauldron_name}
            )
            cauldron = cauldron_result.fetchone()
            
            if not cauldron:
                results["data_diversity"]["issues"].append(f"Cauldron '{cauldron_name}' not found")
                return results
            
            cauldron_id = cauldron[0]
            
            # Get industry diversity
            industry_result = await db.execute(
                """
                SELECT 
                    jsonb_array_elements_text(industries) as industry,
                    COUNT(*) as count
                FROM members 
                WHERE cauldron_id = :cauldron_id
                GROUP BY industry
                ORDER BY count DESC
                """,
                {"cauldron_id": cauldron_id}
            )
            industries = industry_result.fetchall()
            results["data_diversity"]["industries"] = [
                {"industry": ind[0], "member_count": ind[1]} for ind in industries
            ]
            
            # Get story type diversity
            story_type_result = await db.execute(
                """
                SELECT story_type, COUNT(*) as count
                FROM stories 
                WHERE cauldron_id = :cauldron_id
                GROUP BY story_type
                ORDER BY count DESC
                """,
                {"cauldron_id": cauldron_id}
            )
            story_types = story_type_result.fetchall()
            results["data_diversity"]["story_types"] = [
                {"type": st[0], "count": st[1]} for st in story_types
            ]
            
            # Get company diversity
            company_result = await db.execute(
                """
                SELECT company, COUNT(*) as member_count
                FROM members 
                WHERE cauldron_id = :cauldron_id AND company IS NOT NULL
                GROUP BY company
                ORDER BY member_count DESC
                """,
                {"cauldron_id": cauldron_id}
            )
            companies = company_result.fetchall()
            results["data_diversity"]["companies"] = [
                {"company": comp[0], "member_count": comp[1]} for comp in companies
            ]
            
            # Get skill diversity (top 20)
            skill_result = await db.execute(
                """
                SELECT 
                    jsonb_array_elements_text(skills) as skill,
                    COUNT(*) as count
                FROM members 
                WHERE cauldron_id = :cauldron_id
                GROUP BY skill
                ORDER BY count DESC
                LIMIT 20
                """,
                {"cauldron_id": cauldron_id}
            )
            skills = skill_result.fetchall()
            results["data_diversity"]["skills"] = [
                {"skill": skill[0], "member_count": skill[1]} for skill in skills
            ]
            
            # Get geographic diversity
            location_result = await db.execute(
                """
                SELECT location, COUNT(*) as count
                FROM members 
                WHERE cauldron_id = :cauldron_id AND location IS NOT NULL
                GROUP BY location
                ORDER BY count DESC
                """,
                {"cauldron_id": cauldron_id}
            )
            locations = location_result.fetchall()
            results["data_diversity"]["geographic_distribution"] = [
                {"location": loc[0], "member_count": loc[1]} for loc in locations
            ]
            
            # Calculate diversity score
            industry_count = len(results["data_diversity"]["industries"])
            story_type_count = len(results["data_diversity"]["story_types"])
            company_count = len(results["data_diversity"]["companies"])
            location_count = len(results["data_diversity"]["geographic_distribution"])
            
            # Diversity score (out of 100)
            diversity_score = 0
            if industry_count >= 10: diversity_score += 25
            elif industry_count >= 7: diversity_score += 20
            elif industry_count >= 5: diversity_score += 15
            
            if story_type_count >= 5: diversity_score += 25
            elif story_type_count >= 3: diversity_score += 20
            elif story_type_count >= 2: diversity_score += 15
            
            if company_count >= 12: diversity_score += 25
            elif company_count >= 10: diversity_score += 20
            elif company_count >= 8: diversity_score += 15
            
            if location_count >= 12: diversity_score += 25
            elif location_count >= 10: diversity_score += 20
            elif location_count >= 8: diversity_score += 15
            
            results["data_diversity"]["diversity_score"] = diversity_score
            
            # Add issues for low diversity
            if industry_count < 5:
                results["data_diversity"]["issues"].append(f"Low industry diversity: {industry_count} industries")
            if story_type_count < 3:
                results["data_diversity"]["issues"].append(f"Low story type diversity: {story_type_count} types")
            if location_count < 8:
                results["data_diversity"]["issues"].append(f"Low geographic diversity: {location_count} locations")
    
    except Exception as e:
        results["data_diversity"]["issues"].append(f"Diversity check failed: {str(e)}")
    
    return results


async def run_full_validation(cauldron_name: str = "10KSB Demo") -> Dict[str, Any]:
    """Run complete validation suite."""
    
    print("🔍 STONESOUP Seed Data Validation")
    print("=" * 50)
    print(f"Validating cauldron: {cauldron_name}")
    print()
    
    # Run all validation tests
    print("1. Validating database data integrity...")
    db_results = await validate_database_data(cauldron_name)
    
    print("2. Testing semantic search functionality...")
    search_results = await test_semantic_search(cauldron_name)
    
    print("3. Checking data diversity...")
    diversity_results = await check_data_diversity(cauldron_name)
    
    # Combine results
    full_results = {
        **db_results,
        **search_results,
        **diversity_results,
        "validation_summary": {
            "timestamp": datetime.utcnow().isoformat(),
            "cauldron_name": cauldron_name,
            "overall_status": "unknown",
            "critical_issues": [],
            "recommendations": []
        }
    }
    
    # Determine overall status
    all_issues = (
        db_results["database_validation"]["issues"] +
        search_results["semantic_search"]["issues"] +
        diversity_results["data_diversity"]["issues"]
    )
    
    critical_issues = []
    for issue in all_issues:
        if any(keyword in issue.lower() for keyword in ["not found", "no members", "no stories", "failed"]):
            critical_issues.append(issue)
    
    if critical_issues:
        full_results["validation_summary"]["overall_status"] = "failed"
        full_results["validation_summary"]["critical_issues"] = critical_issues
    elif len(all_issues) > 5:
        full_results["validation_summary"]["overall_status"] = "warning"
    else:
        full_results["validation_summary"]["overall_status"] = "passed"
    
    # Generate recommendations
    recommendations = []
    
    if db_results["database_validation"]["member_count"] < 15:
        recommendations.append("Consider running seed script with --clear-existing to ensure all members are created")
    
    if db_results["database_validation"]["members_with_embeddings"] == 0:
        recommendations.append("Run seed script without --skip-embeddings to enable semantic search")
    
    search_quality = search_results["semantic_search"]["embedding_quality"]
    if search_quality.get("pass_percentage", 0) < 60:
        recommendations.append("Semantic search quality is low - check OpenRouter API key and embedding generation")
    
    diversity_score = diversity_results["data_diversity"]["diversity_score"]
    if diversity_score < 70:
        recommendations.append("Data diversity could be improved - consider adding more varied member profiles")
    
    full_results["validation_summary"]["recommendations"] = recommendations
    
    return full_results


def print_validation_report(results: Dict[str, Any]):
    """Print a formatted validation report."""
    
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    # Overall status
    status = results["validation_summary"]["overall_status"]
    status_emoji = "✅" if status == "passed" else "⚠️" if status == "warning" else "❌"
    print(f"\nOverall Status: {status_emoji} {status.upper()}")
    
    # Database validation
    print(f"\n📊 DATABASE VALIDATION")
    db = results["database_validation"]
    print(f"   Cauldron Found: {'✅' if db['cauldron_found'] else '❌'}")
    print(f"   Members: {db['member_count']} created")
    print(f"   Stories: {db['story_count']} created")
    print(f"   Relationships: {db['relationship_count']} created")
    print(f"   Member Embeddings: {db['members_with_embeddings']}/{db['member_count']}")
    print(f"   Story Embeddings: {db['stories_with_embeddings']}/{db['story_count']}")
    
    # Semantic search validation
    print(f"\n🔍 SEMANTIC SEARCH VALIDATION")
    search = results["semantic_search"]
    if "embedding_quality" in search:
        quality = search["embedding_quality"]
        print(f"   Tests Passed: {quality.get('tests_passed', 0)}/{quality.get('total_tests', 0)}")
        print(f"   Pass Rate: {quality.get('pass_percentage', 0)}%")
        print(f"   Quality Rating: {quality.get('quality_rating', 'Unknown')}")
        
        # Show sample query results
        if search["test_queries"]:
            print(f"\n   Sample Query Results:")
            for query in search["test_queries"][:2]:  # Show first 2
                status_icon = "✅" if query.get("passed") else "❌"
                print(f"   {status_icon} '{query['query']}' → {query['results_found']} results")
    
    # Data diversity validation
    print(f"\n🌈 DATA DIVERSITY VALIDATION")
    diversity = results["data_diversity"]
    print(f"   Industries: {len(diversity['industries'])} different")
    print(f"   Story Types: {len(diversity['story_types'])} different")
    print(f"   Companies: {len(diversity['companies'])} different")
    print(f"   Locations: {len(diversity['geographic_distribution'])} different")
    print(f"   Diversity Score: {diversity['diversity_score']}/100")
    
    # Issues
    all_issues = (
        db["issues"] +
        search["issues"] +
        diversity["issues"]
    )
    
    if all_issues:
        print(f"\n⚠️ ISSUES FOUND ({len(all_issues)}):")
        for issue in all_issues:
            print(f"   - {issue}")
    
    # Recommendations
    recommendations = results["validation_summary"]["recommendations"]
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   - {rec}")
    
    print(f"\n{'='*60}")
    print(f"Validation completed at: {results['validation_summary']['timestamp']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate STONESOUP seed data")
    parser.add_argument(
        "--cauldron-name",
        default="10KSB Demo",
        help="Name of the cauldron to validate"
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save detailed results to JSON file"
    )
    
    args = parser.parse_args()
    
    # Run validation
    results = asyncio.run(run_full_validation(args.cauldron_name))
    
    # Print report
    print_validation_report(results)
    
    # Save detailed report if requested
    if args.save_report:
        filename = f"validation_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nDetailed report saved to: {filename}")
    
    # Exit with appropriate code
    status = results["validation_summary"]["overall_status"]
    sys.exit(0 if status == "passed" else 1 if status == "warning" else 2)


if __name__ == "__main__":
    main()