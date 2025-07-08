# STONESOUP Seed Data System

This directory contains a comprehensive seed data generation system for STONESOUP, designed to populate the database with realistic sample data that demonstrates the platform's capabilities for the Goldman Sachs 10,000 Small Businesses program.

## 📋 Overview

The seed system creates:
- **15 diverse member profiles** representing different industries and backgrounds
- **60+ realistic stories** showcasing business achievements, experiences, and case studies
- **AI-powered embeddings** for semantic search capabilities
- **Realistic relationships** between members and stories
- **A complete demonstration workspace** ready for testing and demos

## 🎯 Purpose

This seed data is designed to:
1. **Demonstrate Platform Capabilities**: Show how STONESOUP connects entrepreneurs and facilitates knowledge sharing
2. **Enable Semantic Search**: Test AI-powered search that finds content by meaning, not just keywords
3. **Provide Realistic Examples**: Include actual 10KSB-relevant scenarios and business challenges
4. **Support Development**: Give developers realistic data to work with during feature development
5. **Enable Demos**: Provide compelling data for showcasing the platform to stakeholders

## 📁 File Structure

```
seed_data/
├── __init__.py                 # Package initialization
├── sample_members.py          # Member profile generation
├── sample_stories.py          # Story content generation  
├── embedding_generator.py     # AI embedding utilities
seed_database.py               # Main seeding script
SEED_DATA_README.md           # This documentation
```

## 👥 Sample Members

The seed data includes 15 diverse business owners and entrepreneurs:

### Featured Profiles (10KSB-Specific)
- **Elena Rodriguez** - Restaurant Owner (Mi Cocina Familiar)
- **Marcus Johnson** - Tech Entrepreneur (TechSolutions Co)
- **Sarah Kim** - Manufacturing Owner (Green Manufacturing Solutions)
- **David Thompson** - Construction Contractor (Thompson Custom Builders)

### Additional Profiles Covering
- Healthcare Services (Physical Therapy)
- Professional Services (Accounting)
- E-commerce/Retail (Fashion)
- Transportation/Logistics
- Education/Training
- Agriculture/Food Production
- Beauty/Personal Care
- Financial Services
- Marketing/Advertising
- Automotive Services
- Non-profit/Social Services

Each profile includes:
- Realistic biographical information
- Industry-specific skills and expertise
- Professional background and experience
- Social media and portfolio links
- Detailed business context

## 📖 Sample Stories

Each member has 3-5 stories representing different types:

### Story Types
- **ACHIEVEMENT**: Major business milestones and successes
- **EXPERIENCE**: Project outcomes and professional experiences
- **CASE_STUDY**: Detailed breakdowns of specific initiatives
- **SKILL_DEMONSTRATION**: Examples of expertise in action
- **TESTIMONIAL**: Customer feedback and endorsements
- **THOUGHT_LEADERSHIP**: Industry insights and knowledge sharing

### Example Story Themes
- Business growth and scaling challenges
- Crisis management (e.g., COVID-19 pivots)
- Sustainable business practices
- Technology adoption and digital transformation
- Community engagement and social impact
- Team building and employee retention
- Supply chain optimization
- Customer service excellence

## 🧠 AI Embeddings

### What Are Embeddings?

Embeddings are numerical representations of text that capture semantic meaning. They enable "smart search" that finds relevant content based on meaning rather than just keyword matching.

**Example**: Searching for "restaurant management" will find stories about:
- Food service operations
- Kitchen workflow optimization
- Staff training in hospitality
- Customer experience design

### How STONESOUP Uses Embeddings

1. **Member Profile Embeddings**: Generated from combined bio, skills, expertise, and experience
2. **Story Embeddings**: Created from title, content, summary, and demonstrated skills
3. **Semantic Search**: Find similar members or content using cosine similarity
4. **Content Recommendations**: Suggest relevant stories based on member interests
5. **Skill Matching**: Connect members with complementary expertise

### Technical Details
- **Model**: OpenRouter's `text-embedding-3-small` (1536 dimensions)
- **Provider**: OpenAI via OpenRouter API
- **Storage**: PostgreSQL with pgvector extension
- **Search Method**: Cosine similarity for finding related content

## 🚀 Running the Seed Script

### Prerequisites

1. **Database Setup**
   ```bash
   # Ensure PostgreSQL is running with pgvector extension
   psql -d your_database -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

2. **Environment Variables**
   ```bash
   # Required for embedding generation
   export OPENROUTER_API_KEY="your_openrouter_api_key"
   
   # Optional: Custom database URL
   export DATABASE_URL="postgresql://user:pass@localhost:5432/stonesoup"
   ```

3. **Python Dependencies**
   ```bash
   # Install required packages
   pip install -r requirements.txt
   ```

### Basic Usage

```bash
# Full seeding with embeddings (recommended)
python seed_database.py --clear-existing --verbose

# Quick seeding without embeddings (for development)
python seed_database.py --skip-embeddings --verbose

# Custom cauldron name
python seed_database.py --cauldron-name "My Demo Workspace"
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--clear-existing` | Remove existing data before seeding |
| `--skip-embeddings` | Skip embedding generation (faster, no semantic search) |
| `--cauldron-name` | Name for the demo workspace (default: "10KSB Demo") |
| `--verbose` | Enable detailed logging |
| `--help` | Show help message |

### Example Output

```
2024-01-15 10:30:00 - INFO - STONESOUP Database Seeding Started
2024-01-15 10:30:01 - INFO - ✓ Database connection successful
2024-01-15 10:30:01 - INFO - ✓ OpenRouter API key found
2024-01-15 10:30:02 - INFO - ✓ pgvector extension installed
2024-01-15 10:30:05 - INFO - Created cauldron: 10KSB Demo
2024-01-15 10:30:10 - INFO - Generated 15 member profiles
2024-01-15 10:30:15 - INFO - Generating embeddings for member profiles...
2024-01-15 10:30:45 - INFO - Created 15 members
2024-01-15 10:30:50 - INFO - Generated 63 stories
2024-01-15 10:30:55 - INFO - Generating embeddings for stories...
2024-01-15 10:32:30 - INFO - Created 63 stories
2024-01-15 10:32:35 - INFO - STONESOUP Database Seeding Completed Successfully!
2024-01-15 10:32:35 - INFO - Duration: 155.2 seconds
2024-01-15 10:32:35 - INFO - Members: 15 created
2024-01-15 10:32:35 - INFO - Stories: 63 created
2024-01-15 10:32:35 - INFO - Embeddings: 78 generated
```

## 🔍 Testing Semantic Search

After seeding, you can test the semantic search capabilities:

### Example Searches

1. **"restaurant operations"** - Finds Elena's stories about food service management
2. **"technology startups"** - Discovers Marcus's tech entrepreneurship experiences  
3. **"sustainable manufacturing"** - Locates Sarah's environmental business practices
4. **"crisis management"** - Surfaces COVID-19 pivot stories across multiple members
5. **"team leadership"** - Finds stories about staff management and development

### Search Quality Indicators

Good semantic search results should:
- Find relevant content even without exact keyword matches
- Surface stories from multiple members with similar themes
- Rank results by relevance (similarity score)
- Include diverse story types (achievements, case studies, experiences)

## 📊 Data Statistics

After seeding, you'll have:

| Metric | Count | Details |
|--------|-------|---------|
| **Members** | 15 | Diverse business owners across industries |
| **Stories** | 60+ | 3-5 stories per member |
| **Industries** | 15+ | Restaurant, Tech, Manufacturing, Healthcare, etc. |
| **Skills** | 100+ | Comprehensive business skill taxonomy |
| **Embeddings** | 75+ | AI vectors for semantic search |
| **Companies** | 15 | Realistic business entities |

### Industry Breakdown
- Food Service & Hospitality
- Technology & Software
- Manufacturing & Industrial
- Construction & Real Estate
- Healthcare & Wellness
- Professional Services
- E-commerce & Retail
- Transportation & Logistics
- Education & Training
- Agriculture & Food Production
- Beauty & Personal Care
- Financial Services
- Marketing & Advertising
- Automotive Services
- Non-profit & Social Impact

## 🛠 Development Usage

### For Backend Development
```python
# Access seed data programmatically
from seed_data.sample_members import generate_member_profiles
from seed_data.sample_stories import get_all_sample_stories

members = generate_member_profiles()
stories = get_all_sample_stories("your-cauldron-id")
```

### For Testing
```python
# Test with specific member data
from seed_data.sample_members import get_member_by_email

elena = get_member_by_email("elena.rodriguez@micocina.com")
marcus = get_member_by_email("marcus@techsolutions.co")
```

### For Embedding Development
```python
# Generate custom embeddings
from seed_data.embedding_generator import EmbeddingGenerator

generator = EmbeddingGenerator()
embedding = await generator.generate_embedding("your text here")
```

## 🔧 Customization

### Adding New Members
1. Edit `seed_data/sample_members.py`
2. Add new member dictionaries to the `generate_member_profiles()` function
3. Include realistic business details and skills

### Adding New Stories
1. Edit `seed_data/sample_stories.py`
2. Add story templates or specific stories for members
3. Ensure stories include proper metadata (tags, skills, etc.)

### Modifying Embeddings
1. Edit `seed_data/embedding_generator.py`
2. Adjust text preparation logic for better semantic representation
3. Modify embedding model or parameters

## 🐛 Troubleshooting

### Common Issues

**"OpenRouter API key not found"**
```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

**"pgvector extension not installed"**
```sql
CREATE EXTENSION vector;
```

**"Database connection failed"**
- Check DATABASE_URL environment variable
- Ensure PostgreSQL is running
- Verify connection credentials

**"Embedding generation slow"**
- Use `--skip-embeddings` for faster development
- Check internet connection for API calls
- Consider caching with local development

### Performance Tips

1. **Use Caching**: Embeddings are cached locally to avoid regeneration
2. **Skip Embeddings**: Use `--skip-embeddings` during development
3. **Batch Processing**: The script automatically batches API calls
4. **Clean Existing**: Use `--clear-existing` to avoid duplicates

## 📝 Logging

The script generates detailed logs:
- **Console Output**: Real-time progress and status
- **Log File**: `seed_database.log` with full details
- **Summary Report**: JSON report with statistics

## 🤝 Contributing

To contribute to the seed data system:

1. **Add Industry Expertise**: Create new member profiles for underrepresented industries
2. **Improve Story Quality**: Add more detailed, realistic business scenarios
3. **Enhance Embeddings**: Optimize text preparation for better semantic search
4. **Add Validation**: Implement additional data quality checks

## 📞 Support

For issues with the seed data system:
1. Check the troubleshooting section above
2. Review the generated log files for error details
3. Ensure all prerequisites are properly configured
4. Test with `--skip-embeddings` to isolate embedding-related issues

---

**Generated by**: STONESOUP Seed Data System v1.0.0  
**Last Updated**: January 2024  
**Compatible with**: STONESOUP Backend v0.1.0