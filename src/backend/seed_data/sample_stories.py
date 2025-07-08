"""
Sample story data for STONESOUP seed generation.

This module contains realistic story data for each member profile, showcasing
different types of business achievements, experiences, and case studies that
would be relevant for Goldman Sachs 10,000 Small Businesses program participants.

Story types included:
- ACHIEVEMENT: Specific accomplishments and milestones
- EXPERIENCE: Work experiences and project outcomes
- CASE_STUDY: Detailed project breakdowns with results
- SKILL_DEMONSTRATION: Examples of specific skills in action
- TESTIMONIAL: Client/customer endorsements and feedback
- THOUGHT_LEADERSHIP: Insights and industry knowledge

Each story includes:
- Compelling title and detailed content
- Relevant tags and skills demonstrated
- Realistic timelines and outcomes
- Company/organization context
- Professional writing style suitable for business networking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

# Import the story type enums
from app.models.story import StoryType, StoryStatus


def generate_stories_for_member(member: Dict[str, Any], cauldron_id: str) -> List[Dict[str, Any]]:
    """
    Generate 3-5 realistic stories for a specific member.
    
    Args:
        member: Member profile dictionary
        cauldron_id: The cauldron ID for multi-tenancy
        
    Returns:
        List of story dictionaries for the member
    """
    # Story templates based on member's industry and role
    stories = []
    
    # Elena Rodriguez - Restaurant Owner
    if member["email"] == "elena.rodriguez@micocina.com":
        stories = [
            {
                "title": "From Food Truck to Full Restaurant: A Journey of Growth",
                "content": """When I started Mi Cocina Familiar with just a food truck in 2016, I never imagined I'd be serving 200+ customers daily in my own restaurant. 

The journey began when I realized there was a gap in authentic Mexican cuisine in our Austin neighborhood. Starting with $15,000 in savings and a used food truck, I began serving traditional recipes passed down from my grandmother.

**The Challenge**: Building a customer base while maintaining food quality and managing costs on a tight budget.

**The Solution**: I focused on three key strategies:
1. **Authentic Recipes**: Never compromising on traditional flavors and preparation methods
2. **Community Engagement**: Participating in local festivals and building relationships with regular customers
3. **Sustainable Sourcing**: Partnering with local farms for fresh ingredients, which also supported our community

**The Results**: 
- Grew from 20 daily customers to 200+ 
- Increased revenue by 400% over 18 months
- Opened our brick-and-mortar location in 2018
- Created 12 local jobs
- Established partnerships with 5 local farms

**Key Learnings**: Success in the restaurant business isn't just about good food—it's about building genuine connections with your community while staying true to your values. The investment in local sourcing not only improved our food quality but also created a story our customers connected with.""",
                "summary": "Grew from food truck to full restaurant serving 200+ daily customers through authentic cuisine, community engagement, and sustainable local sourcing.",
                "story_type": StoryType.ACHIEVEMENT,
                "status": StoryStatus.PUBLISHED,
                "tags": ["Restaurant Growth", "Community Building", "Sustainable Business", "Local Sourcing", "Food Service"],
                "skills_demonstrated": ["Restaurant Management", "Community Engagement", "Sustainable Sourcing", "Business Growth", "Customer Service"],
                "company": "Mi Cocina Familiar",
                "external_url": "https://micocinafamiliar.com/our-story",
                "occurred_at": datetime.utcnow() - timedelta(days=365*2)
            },
            {
                "title": "Navigating COVID-19: Pivoting to Takeout and Delivery",
                "content": """When COVID-19 hit in March 2020, our restaurant faced an immediate 80% drop in revenue as dining restrictions were implemented. Like many restaurant owners, I had to make quick, difficult decisions to keep the business alive.

**The Crisis**: Overnight, we went from a bustling dine-in restaurant to an empty space. Fixed costs remained the same, but revenue plummeted.

**The Pivot Strategy**:
1. **Rapid Technology Adoption**: Implemented online ordering system within 48 hours
2. **Menu Optimization**: Redesigned menu for takeout-friendly items that traveled well
3. **Staff Cross-Training**: Trained servers to handle phone orders and packaging
4. **Community Outreach**: Launched family meal packages and donation program for healthcare workers

**Financial Management**:
- Negotiated payment plans with suppliers
- Applied for PPP loans to retain all staff
- Implemented cost-control measures without compromising quality
- Diversified revenue streams with meal kits and catering

**The Outcome**:
- Maintained 90% of staff throughout the pandemic
- Delivery and takeout became 60% of business (previously 20%)
- Developed new revenue streams generating $2,000/month
- Strengthened community relationships through donation program

**Lessons Learned**: Crisis management requires both quick decision-making and long-term thinking. The technology and systems we implemented during COVID actually made us more efficient and opened new revenue opportunities we continue to use today.""",
                "summary": "Successfully pivoted restaurant operations during COVID-19, maintaining 90% of staff and developing new revenue streams through digital transformation.",
                "story_type": StoryType.CASE_STUDY,
                "status": StoryStatus.PUBLISHED,
                "tags": ["Crisis Management", "Digital Transformation", "Staff Retention", "Revenue Diversification", "Community Support"],
                "skills_demonstrated": ["Crisis Management", "Technology Adoption", "Staff Management", "Financial Planning", "Community Relations"],
                "company": "Mi Cocina Familiar",
                "occurred_at": datetime.utcnow() - timedelta(days=365*1)
            },
            {
                "title": "Building a Sustainable Supply Chain with Local Farmers",
                "content": """One of our biggest achievements has been developing a sustainable supply chain that supports local farmers while ensuring consistent quality for our restaurant.

**The Challenge**: Balancing cost control with quality ingredients while supporting our community values.

**The Approach**:
We partnered with 5 local farms within 50 miles of Austin:
- Green Valley Organic (vegetables and herbs)
- Hill Country Cattle (grass-fed beef)
- Sunrise Poultry (free-range chicken)
- Austin Urban Farms (microgreens and specialty items)
- Heritage Pork Co. (sustainable pork)

**Implementation**:
- Developed weekly ordering system with guaranteed minimums
- Adjusted menu seasonally based on local availability
- Created farm-to-table story for each dish
- Trained staff on sourcing story for customer education

**Results**:
- Reduced food costs by 15% through direct sourcing
- Improved food quality and freshness
- Created marketing advantage with farm-to-table story
- Supported local economy with $75,000 annual purchases
- Reduced environmental impact through shorter supply chain

**Customer Impact**: Our customers love knowing their meal supports local farmers. It's become a key differentiator and driver of customer loyalty.""",
                "summary": "Developed sustainable supply chain with 5 local farms, reducing costs 15% while improving quality and supporting community.",
                "story_type": StoryType.EXPERIENCE,
                "status": StoryStatus.PUBLISHED,
                "tags": ["Supply Chain", "Local Sourcing", "Sustainability", "Cost Control", "Community Partnership"],
                "skills_demonstrated": ["Supply Chain Management", "Vendor Relations", "Sustainability", "Cost Control", "Community Building"],
                "company": "Mi Cocina Familiar",
                "occurred_at": datetime.utcnow() - timedelta(days=180)
            },
            {
                "title": "Training and Retaining Great Restaurant Staff",
                "content": """In an industry known for high turnover, we've maintained an 85% staff retention rate by investing in our team's growth and creating a positive work environment.

**Our Training Program**:
- 40-hour comprehensive onboarding for all positions
- Monthly skill development workshops
- Cross-training opportunities
- Leadership development for senior staff

**Key Retention Strategies**:
1. **Competitive Benefits**: Health insurance, paid time off, meal benefits
2. **Career Development**: Clear advancement paths and skill building
3. **Recognition Programs**: Employee of the month, performance bonuses
4. **Work-Life Balance**: Flexible scheduling, no split shifts

**Results**:
- 85% retention rate (industry average: 40%)
- 3 team members promoted to management roles
- Reduced hiring and training costs by $12,000 annually
- Improved customer service scores by 25%
- Created a positive workplace culture that attracts quality candidates

**The Impact**: Our low turnover means better customer service, lower costs, and a more experienced team. Several of our staff have gone on to open their own restaurants, and we're proud to have been part of their journey.""",
                "summary": "Achieved 85% staff retention rate through comprehensive training, competitive benefits, and career development programs.",
                "story_type": StoryType.SKILL_DEMONSTRATION,
                "status": StoryStatus.PUBLISHED,
                "tags": ["Staff Training", "Employee Retention", "Human Resources", "Leadership Development", "Workplace Culture"],
                "skills_demonstrated": ["Staff Training", "Employee Retention", "Leadership Development", "Human Resources", "Team Building"],
                "company": "Mi Cocina Familiar",
                "occurred_at": datetime.utcnow() - timedelta(days=90)
            }
        ]
    
    # Marcus Johnson - Tech Entrepreneur
    elif member["email"] == "marcus@techsolutions.co":
        stories = [
            {
                "title": "Building an AI-Powered Customer Service Platform for Small Businesses",
                "content": """TechSolutions Co's flagship product, ChatBot Pro, has transformed how 150+ small businesses handle customer service by providing 24/7 support at a fraction of traditional costs.

**The Problem**: Small businesses struggle to provide consistent customer service due to limited resources and staffing constraints. They can't afford enterprise-level solutions but need more than basic chatbots.

**The Solution**: We developed an AI-powered platform that:
- Learns from each business's specific products and services
- Integrates with existing CRM and support systems
- Provides human handoff for complex issues
- Offers multilingual support for diverse customer bases

**Technical Implementation**:
- Built on OpenAI's GPT architecture with custom training
- Developed proprietary knowledge base integration
- Created intuitive dashboard for business owners
- Implemented usage analytics and performance tracking

**Results**:
- 150+ small businesses using the platform
- Average 40% reduction in customer service costs
- 24/7 support availability for all clients
- 95% customer satisfaction rating
- $500K ARR within 18 months

**Key Innovation**: The platform's ability to learn each business's unique context while maintaining enterprise-level functionality at small business prices.

**Impact**: Our clients report not only cost savings but improved customer satisfaction because they can now provide consistent, 24/7 support that would have been impossible with traditional staffing.""",
                "summary": "Developed AI-powered customer service platform serving 150+ small businesses with 40% cost reduction and 95% satisfaction rating.",
                "story_type": StoryType.ACHIEVEMENT,
                "status": StoryStatus.PUBLISHED,
                "tags": ["AI Development", "Customer Service", "Small Business Solutions", "Product Development", "SaaS"],
                "skills_demonstrated": ["AI Development", "Product Management", "Customer Service", "Business Development", "Software Architecture"],
                "company": "TechSolutions Co",
                "external_url": "https://techsolutions.co/chatbot-pro",
                "occurred_at": datetime.utcnow() - timedelta(days=365*2)
            },
            {
                "title": "From Startup to Exit: Lessons from Building and Selling DataSync",
                "content": """In 2019, I successfully sold DataSync, a data integration platform, to a Fortune 500 company for $2.3M after building it from idea to product-market fit in just 2 years.

**The Journey**:
DataSync started as a solution to a problem I experienced firsthand: small businesses struggling to integrate data across multiple software tools.

**Building the Product**:
- Identified core integration needs through 50+ customer interviews
- Developed MVP in 6 months with a team of 3 developers
- Focused on top 10 small business software integrations
- Implemented freemium model to drive adoption

**Growth Strategy**:
- Partner channel strategy with accountants and consultants
- Content marketing focused on small business data challenges
- Referral program that generated 40% of new customers
- Customer success program with 95% retention rate

**Key Metrics at Exit**:
- 500+ active customers
- $300K ARR with 15% monthly growth
- 95% customer retention rate
- 40% of customers upgraded to paid plans
- Team of 8 employees

**The Sale Process**:
- Approached by acquirer who was our customer
- 6-month due diligence process
- Negotiated earnout based on integration success
- Ensured all employees were retained with increases

**Lessons Learned**:
1. **Customer Focus**: Every decision was driven by customer needs
2. **Scalable Architecture**: Built for growth from day one
3. **Financial Discipline**: Maintained profitability throughout
4. **Team Investment**: Great team made the difference
5. **Market Timing**: Caught the integration wave at the right time

**Post-Exit**: Used the experience and capital to start TechSolutions Co, applying these lessons to build an even better company.""",
                "summary": "Successfully built and sold DataSync for $2.3M in 2 years, serving 500+ customers with 95% retention rate.",
                "story_type": StoryType.CASE_STUDY,
                "status": StoryStatus.PUBLISHED,
                "tags": ["Startup Exit", "Data Integration", "Product Development", "Business Growth", "M&A"],
                "skills_demonstrated": ["Startup Strategy", "Product Development", "Business Development", "Financial Management", "Team Building"],
                "company": "DataSync (Acquired)",
                "occurred_at": datetime.utcnow() - timedelta(days=365*3)
            },
            {
                "title": "Mentoring Underrepresented Founders: Building the Next Generation",
                "content": """Over the past 3 years, I've mentored 25 underrepresented founders through formal programs and informal relationships, helping them raise over $1.2M in funding and build sustainable businesses.

**The Program**:
Through the Atlanta Tech Diversity Initiative, I commit 10 hours per month to mentoring Black and Latino founders in the tech space.

**My Approach**:
- **Practical Guidance**: Focus on actionable advice over theoretical concepts
- **Network Access**: Introduce founders to potential customers, investors, and partners
- **Skill Development**: Weekly workshops on fundraising, product development, and scaling
- **Accountability**: Monthly check-ins with specific goals and metrics

**Success Stories**:
- **Sarah's EdTech Startup**: Helped secure $150K seed funding and first enterprise client
- **Carlos's Logistics App**: Assisted with product-market fit and $75K revenue milestone
- **Aisha's FinTech Platform**: Supported through regulatory challenges and launched successfully

**Results**:
- 25 founders mentored
- $1.2M total funding raised by mentees
- 18 companies still operating and growing
- 5 founders became profitable within 18 months
- 3 mentees now mentor others (paying it forward)

**Key Insights**:
1. **Access to Networks**: Often the biggest barrier for underrepresented founders
2. **Practical Experience**: Real-world experience trumps theoretical knowledge
3. **Confidence Building**: Many talented founders just need validation and support
4. **Systemic Change**: Individual mentoring drives broader ecosystem change

**Personal Impact**: This work has been as rewarding as building my own companies. Seeing founders succeed and then help others creates a multiplying effect that transforms entire communities.""",
                "summary": "Mentored 25 underrepresented founders who raised $1.2M+ in funding, with 18 companies still operating and growing.",
                "story_type": StoryType.THOUGHT_LEADERSHIP,
                "status": StoryStatus.PUBLISHED,
                "tags": ["Mentorship", "Diversity & Inclusion", "Entrepreneurship", "Community Impact", "Tech Ecosystem"],
                "skills_demonstrated": ["Mentorship", "Community Building", "Fundraising", "Network Building", "Leadership Development"],
                "company": "Atlanta Tech Diversity Initiative",
                "occurred_at": datetime.utcnow() - timedelta(days=90)
            }
        ]
    
    # Sarah Kim - Manufacturing
    elif member["email"] == "sarah.kim@greenmanufacturing.com":
        stories = [
            {
                "title": "Implementing Lean Manufacturing: 30% Efficiency Improvement",
                "content": """At Green Manufacturing Solutions, we implemented lean manufacturing principles that resulted in a 30% efficiency improvement and $200K annual cost savings.

**The Challenge**: Our production line was plagued with bottlenecks, waste, and inconsistent quality. We were losing money on several contracts due to inefficiencies.

**The Lean Implementation**:
1. **Value Stream Mapping**: Identified 7 major waste sources in our process
2. **5S Methodology**: Organized workspace for maximum efficiency
3. **Kanban System**: Implemented pull-based production scheduling
4. **Continuous Improvement**: Weekly kaizen events with all staff

**Key Changes**:
- Reduced setup time from 45 minutes to 12 minutes
- Eliminated 3 redundant quality check points
- Reorganized floor layout to minimize material handling
- Implemented predictive maintenance schedule

**Results**:
- 30% increase in production efficiency
- 50% reduction in work-in-process inventory
- 25% improvement in on-time delivery
- $200K annual cost savings
- 40% reduction in defect rate

**Team Impact**: Employees became actively engaged in improvement process, contributing 150+ improvement suggestions in the first year.

**Long-term Benefits**: The lean culture we created continues to drive improvements. We're now consulting other manufacturers on lean implementation.""",
                "summary": "Implemented lean manufacturing principles achieving 30% efficiency improvement and $200K annual cost savings.",
                "story_type": StoryType.ACHIEVEMENT,
                "status": StoryStatus.PUBLISHED,
                "tags": ["Lean Manufacturing", "Process Improvement", "Cost Reduction", "Quality Control", "Operational Excellence"],
                "skills_demonstrated": ["Process Optimization", "Lean Manufacturing", "Quality Control", "Cost Analysis", "Team Leadership"],
                "company": "Green Manufacturing Solutions",
                "occurred_at": datetime.utcnow() - timedelta(days=365*1)
            },
            {
                "title": "Achieving Zero Waste Manufacturing: Environmental and Economic Success",
                "content": """Our journey to zero waste manufacturing not only aligned with our environmental values but also generated $150K in annual savings and opened new revenue streams.

**The Vision**: Eliminate all waste from our manufacturing process while maintaining profitability and quality.

**The Strategy**:
1. **Waste Audit**: Comprehensive analysis of all waste streams
2. **Material Optimization**: Redesigned processes to minimize waste
3. **Recycling Programs**: Partnerships with local recycling facilities
4. **By-product Sales**: Turned waste into revenue streams

**Implementation Phases**:
- Phase 1: Reduced waste by 60% through process optimization
- Phase 2: Implemented closed-loop recycling systems
- Phase 3: Developed markets for all by-products
- Phase 4: Achieved certified zero waste to landfill status

**Results**:
- 100% waste diversion from landfills
- $150K annual savings in waste disposal costs
- $75K annual revenue from by-product sales
- 25% reduction in raw material costs
- Oregon DEQ Environmental Excellence Award

**Innovation**: Developed proprietary method for recycling composite materials that other manufacturers now license.

**Market Impact**: Our zero waste certification has become a competitive advantage, with 40% of new customers citing environmental practices as a decision factor.""",
                "summary": "Achieved zero waste manufacturing status, generating $150K annual savings and $75K in new revenue from by-products.",
                "story_type": StoryType.CASE_STUDY,
                "status": StoryStatus.PUBLISHED,
                "tags": ["Sustainability", "Zero Waste", "Environmental Manufacturing", "Cost Savings", "Innovation"],
                "skills_demonstrated": ["Sustainability", "Environmental Compliance", "Process Innovation", "Cost Analysis", "Revenue Generation"],
                "company": "Green Manufacturing Solutions",
                "occurred_at": datetime.utcnow() - timedelta(days=180)
            }
        ]
    
    # Add more member stories following the same pattern...
    # For brevity, I'll add a few more key members and then create a generic story generator
    
    # David Thompson - Construction
    elif member["email"] == "david@thompsonbuilders.com":
        stories = [
            {
                "title": "Managing a $2M Commercial Renovation Under Tight Deadline",
                "content": """When a local hospital needed to renovate their emergency department without closing, we delivered a $2M renovation project in 6 months while maintaining full hospital operations.

**The Challenge**: 
- 24/7 hospital operations couldn't be interrupted
- Strict healthcare regulations and safety requirements
- Tight 6-month deadline before new equipment installation
- Complex coordination with medical staff and multiple contractors

**Project Management Approach**:
1. **Phased Construction**: Divided project into 4 phases to maintain operations
2. **Off-hours Scheduling**: Noisy work limited to specific hours
3. **Infection Control**: Implemented hospital-grade dust and contamination protocols
4. **Safety Protocols**: Enhanced safety measures due to active medical environment

**Key Innovations**:
- Modular construction techniques to minimize on-site disruption
- Advanced air filtration systems during construction
- Real-time communication system with hospital staff
- Prefabricated components to reduce installation time

**Results**:
- Project completed 2 weeks ahead of schedule
- Zero safety incidents during construction
- 100% compliance with healthcare regulations
- Client satisfaction score: 9.8/10
- Emergency department reopened with 30% increased capacity

**Long-term Impact**: This project established us as the go-to contractor for healthcare facilities in the region, leading to $5M in additional contracts.""",
                "summary": "Delivered $2M hospital renovation in 6 months without disrupting operations, completed ahead of schedule with zero safety incidents.",
                "story_type": StoryType.ACHIEVEMENT,
                "status": StoryStatus.PUBLISHED,
                "tags": ["Healthcare Construction", "Project Management", "Commercial Renovation", "Safety Management", "Complex Projects"],
                "skills_demonstrated": ["Construction Management", "Project Planning", "Safety Management", "Client Relations", "Healthcare Compliance"],
                "company": "Thompson Custom Builders",
                "occurred_at": datetime.utcnow() - timedelta(days=180)
            }
        ]
    
    else:
        # Generate generic stories for other members
        stories = generate_generic_stories(member, cauldron_id)
    
    # Add common fields and randomize dates
    for story in stories:
        story["cauldron_id"] = cauldron_id
        story["ai_generated"] = False
        story["confidence_score"] = None
        story["generation_prompt"] = None
        story["view_count"] = random.randint(10, 200)
        story["like_count"] = random.randint(0, 50)
        story["reviewed_by_id"] = None
        story["reviewed_at"] = None
        story["review_notes"] = None
        story["extra_metadata"] = {
            "reading_time": random.randint(3, 8),
            "complexity_level": random.choice(["beginner", "intermediate", "advanced"]),
            "industry_relevance": random.choice(["high", "medium", "low"]),
            "engagement_score": random.randint(70, 95)
        }
        
        # Set published date if status is published
        if story["status"] == StoryStatus.PUBLISHED:
            story["published_at"] = story["occurred_at"] + timedelta(days=random.randint(1, 30))
    
    return stories


def generate_generic_stories(member: Dict[str, Any], cauldron_id: str) -> List[Dict[str, Any]]:
    """Generate generic stories for members without specific templates."""
    
    # Story templates based on common business themes
    story_templates = [
        {
            "title_template": "Overcoming {challenge} in {industry}",
            "content_template": """In my role as {title} at {company}, I faced a significant challenge with {challenge}. Here's how I addressed it:

**The Challenge**: {challenge_description}

**My Approach**:
1. Analyzed the root cause through {analysis_method}
2. Developed a strategic plan involving {solution_approach}
3. Implemented changes over {timeframe}
4. Monitored progress using {metrics}

**Results**:
- {result_1}
- {result_2}
- {result_3}

**Key Learnings**: {key_learning}

This experience taught me the importance of {lesson} and has influenced how I approach similar challenges in the future.""",
            "story_type": StoryType.EXPERIENCE,
            "tags": ["Problem Solving", "Leadership", "Business Growth", "Strategy"]
        },
        {
            "title_template": "Building {skill} Capabilities at {company}",
            "content_template": """Developing {skill} capabilities has been crucial to our success at {company}. Here's how we built this competency:

**The Need**: {business_need}

**Our Development Strategy**:
- {strategy_point_1}
- {strategy_point_2}
- {strategy_point_3}

**Implementation**:
{implementation_details}

**Results**:
- {measurable_result_1}
- {measurable_result_2}
- {impact_on_business}

**Lessons Learned**: {key_insight}

This capability now serves as a competitive advantage and has opened new opportunities for growth.""",
            "story_type": StoryType.SKILL_DEMONSTRATION,
            "tags": ["Skill Development", "Capability Building", "Competitive Advantage", "Growth"]
        },
        {
            "title_template": "Customer Success: {specific_achievement}",
            "content_template": """One of our most rewarding customer success stories involved {customer_situation}. Here's how we delivered exceptional results:

**The Situation**: {customer_challenge}

**Our Solution**:
{solution_description}

**Implementation Process**:
1. {step_1}
2. {step_2}
3. {step_3}

**Results for the Customer**:
- {customer_result_1}
- {customer_result_2}
- {customer_result_3}

**What Made the Difference**: {differentiator}

This success led to {follow_up_opportunity} and demonstrates our commitment to {company_value}.""",
            "story_type": StoryType.TESTIMONIAL,
            "tags": ["Customer Success", "Client Relations", "Results Delivery", "Value Creation"]
        }
    ]
    
    # Generate 3-4 stories using templates
    stories = []
    templates_to_use = random.sample(story_templates, min(3, len(story_templates)))
    
    for template in templates_to_use:
        story = generate_story_from_template(template, member, cauldron_id)
        stories.append(story)
    
    return stories


def generate_story_from_template(template: Dict[str, Any], member: Dict[str, Any], cauldron_id: str) -> Dict[str, Any]:
    """Generate a specific story from a template and member data."""
    
    # Extract member details
    title = member.get("title", "Business Owner")
    company = member.get("company", "My Company")
    industry = member["industries"][0] if member["industries"] else "Business"
    skills = member["skills"]
    expertise = member["expertise_areas"]
    
    # Create story content based on template
    story_vars = {
        "title": title,
        "company": company,
        "industry": industry,
        "challenge": random.choice([
            "operational efficiency",
            "customer acquisition",
            "process optimization",
            "market expansion",
            "quality improvement",
            "cost management"
        ]),
        "skill": random.choice(skills) if skills else "business development",
        "specific_achievement": random.choice([
            "Exceeding Customer Expectations",
            "Delivering Complex Project",
            "Solving Critical Issue",
            "Building Long-term Partnership"
        ])
    }
    
    # Fill in template variables
    title = template["title_template"].format(**story_vars)
    content = template["content_template"].format(**story_vars)
    
    # Generate realistic story details
    story = {
        "title": title,
        "content": content,
        "summary": f"Story about {story_vars['challenge']} in {industry} industry, demonstrating {story_vars['skill']} capabilities.",
        "story_type": template["story_type"],
        "status": StoryStatus.PUBLISHED,
        "tags": template["tags"] + [industry, company],
        "skills_demonstrated": random.sample(skills, min(3, len(skills))) if skills else ["Business Management"],
        "company": company,
        "external_url": None,
        "occurred_at": datetime.utcnow() - timedelta(days=random.randint(30, 730))
    }
    
    return story


def get_all_sample_stories(cauldron_id: str) -> List[Dict[str, Any]]:
    """
    Get all sample stories for all members.
    
    Args:
        cauldron_id: The cauldron ID for multi-tenancy
        
    Returns:
        List of all story dictionaries
    """
    from .sample_members import generate_member_profiles
    
    all_stories = []
    members = generate_member_profiles()
    
    for member in members:
        member_stories = generate_stories_for_member(member, cauldron_id)
        all_stories.extend(member_stories)
    
    return all_stories


def get_stories_by_type(story_type: StoryType, cauldron_id: str) -> List[Dict[str, Any]]:
    """Get all stories of a specific type."""
    all_stories = get_all_sample_stories(cauldron_id)
    return [story for story in all_stories if story["story_type"] == story_type]


def get_stories_by_member_email(email: str, cauldron_id: str) -> List[Dict[str, Any]]:
    """Get all stories for a specific member."""
    from .sample_members import get_member_by_email
    
    try:
        member = get_member_by_email(email)
        return generate_stories_for_member(member, cauldron_id)
    except ValueError:
        return []


if __name__ == "__main__":
    # Test the story generation
    from .sample_members import generate_member_profiles
    
    members = generate_member_profiles()
    test_cauldron = "test-cauldron-id"
    
    total_stories = 0
    for member in members[:3]:  # Test first 3 members
        stories = generate_stories_for_member(member, test_cauldron)
        total_stories += len(stories)
        print(f"{member['name']}: {len(stories)} stories")
    
    print(f"Total stories generated: {total_stories}")