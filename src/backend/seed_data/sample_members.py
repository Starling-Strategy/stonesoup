"""
Sample member data for STONESOUP seed generation.

This module contains realistic member profiles focused on business and workforce
development themes that would be relevant for Goldman Sachs 10,000 Small Businesses
program participants. Each member represents a different industry, background, and
career stage to demonstrate the diversity and search capabilities of the platform.

The profiles include:
- Basic information (name, email, location, etc.)
- Professional background (title, company, experience)
- Skills and expertise areas
- Industry classifications
- Social/portfolio links
- Biographical information

All data is fictional but realistic, representing the types of entrepreneurs
and business leaders who would benefit from Goldman Sachs 10KSB programs.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import random


def generate_member_profiles() -> List[Dict[str, Any]]:
    """
    Generate diverse member profiles for seeding.
    
    Returns a list of member dictionaries with realistic business/workforce
    development focused profiles. Each profile includes all necessary fields
    for the Member model including skills, expertise, and biographical data.
    
    Returns:
        List[Dict[str, Any]]: List of member profile dictionaries
    """
    
    # Core member profiles - mix of industries and backgrounds
    members = [
        {
            # Elena Rodriguez - Restaurant Owner (from PRD)
            "name": "Elena Rodriguez",
            "email": "elena.rodriguez@micocina.com",
            "username": "elena_rodriguez",
            "clerk_user_id": "user_elena_rodriguez_001",
            "title": "Owner & Head Chef",
            "company": "Mi Cocina Familiar",
            "bio": "Passionate restaurateur bringing authentic Mexican cuisine to the community. Started with a food truck and grew to a full restaurant serving 200+ customers daily. Focused on sustainable sourcing and supporting local farmers.",
            "location": "Austin, Texas",
            "timezone": "America/Chicago",
            "years_of_experience": 8.5,
            "hourly_rate": 125.0,
            "skills": [
                "Restaurant Management",
                "Food Safety & Compliance",
                "Menu Development",
                "Cost Control",
                "Staff Training",
                "Customer Service",
                "Inventory Management",
                "Vendor Relations",
                "Financial Planning",
                "Marketing & Promotion"
            ],
            "expertise_areas": [
                "Restaurant Operations",
                "Culinary Arts",
                "Small Business Management",
                "Hispanic Market",
                "Food & Beverage",
                "Hospitality"
            ],
            "industries": [
                "Food Service",
                "Hospitality",
                "Small Business",
                "Retail"
            ],
            "linkedin_url": "https://linkedin.com/in/elena-rodriguez-chef",
            "website_url": "https://micocinafamiliar.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Marcus Johnson - Tech Entrepreneur
            "name": "Marcus Johnson",
            "email": "marcus@techsolutions.co",
            "username": "marcus_johnson",
            "clerk_user_id": "user_marcus_johnson_002",
            "title": "Founder & CEO",
            "company": "TechSolutions Co",
            "bio": "Serial entrepreneur with 12+ years in tech. Founded three startups, two successful exits. Currently building AI-powered solutions for small businesses. Mentor for underrepresented founders in tech.",
            "location": "Atlanta, Georgia",
            "timezone": "America/New_York",
            "years_of_experience": 12.0,
            "hourly_rate": 200.0,
            "skills": [
                "Software Development",
                "Product Management",
                "AI & Machine Learning",
                "Startup Strategy",
                "Fundraising",
                "Team Building",
                "Business Development",
                "Market Research",
                "Financial Modeling",
                "Pitch Deck Creation"
            ],
            "expertise_areas": [
                "Technology Startups",
                "Artificial Intelligence",
                "Business Strategy",
                "Venture Capital",
                "Product Development",
                "Team Leadership"
            ],
            "industries": [
                "Technology",
                "Software",
                "Artificial Intelligence",
                "Startups"
            ],
            "linkedin_url": "https://linkedin.com/in/marcus-johnson-tech",
            "github_url": "https://github.com/marcusjohnson",
            "website_url": "https://techsolutions.co",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Sarah Kim - Manufacturing Business
            "name": "Sarah Kim",
            "email": "sarah.kim@greenmanufacturing.com",
            "username": "sarah_kim",
            "clerk_user_id": "user_sarah_kim_003",
            "title": "President & Owner",
            "company": "Green Manufacturing Solutions",
            "bio": "Industrial engineer turned business owner. Built a sustainable manufacturing company from the ground up, focusing on eco-friendly production methods. Passionate about bringing manufacturing jobs back to American communities.",
            "location": "Portland, Oregon",
            "timezone": "America/Los_Angeles",
            "years_of_experience": 15.0,
            "hourly_rate": 175.0,
            "skills": [
                "Manufacturing Operations",
                "Process Optimization",
                "Quality Control",
                "Supply Chain Management",
                "Environmental Compliance",
                "Lean Manufacturing",
                "Project Management",
                "Cost Analysis",
                "Vendor Management",
                "Regulatory Affairs"
            ],
            "expertise_areas": [
                "Manufacturing",
                "Sustainability",
                "Operations Management",
                "Quality Assurance",
                "Industrial Engineering",
                "Green Technology"
            ],
            "industries": [
                "Manufacturing",
                "Sustainability",
                "Industrial",
                "Green Technology"
            ],
            "linkedin_url": "https://linkedin.com/in/sarah-kim-manufacturing",
            "website_url": "https://greenmanufacturing.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # David Thompson - Construction/Real Estate
            "name": "David Thompson",
            "email": "david@thompsonbuilders.com",
            "username": "david_thompson",
            "clerk_user_id": "user_david_thompson_004",
            "title": "General Contractor & Owner",
            "company": "Thompson Custom Builders",
            "bio": "Third-generation builder specializing in custom homes and commercial renovations. Committed to quality craftsmanship and sustainable building practices. Active in local business development initiatives.",
            "location": "Nashville, Tennessee",
            "timezone": "America/Chicago",
            "years_of_experience": 20.0,
            "hourly_rate": 150.0,
            "skills": [
                "Construction Management",
                "Project Planning",
                "Building Codes",
                "Cost Estimation",
                "Client Relations",
                "Subcontractor Management",
                "Quality Control",
                "Safety Management",
                "Permit Processing",
                "Budget Management"
            ],
            "expertise_areas": [
                "Construction",
                "Real Estate Development",
                "Project Management",
                "Building Codes",
                "Sustainable Building",
                "Commercial Construction"
            ],
            "industries": [
                "Construction",
                "Real Estate",
                "Building Materials",
                "Architecture"
            ],
            "linkedin_url": "https://linkedin.com/in/david-thompson-builder",
            "website_url": "https://thompsonbuilders.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Priya Patel - Healthcare Services
            "name": "Priya Patel",
            "email": "priya.patel@wellnesscenter.com",
            "username": "priya_patel",
            "clerk_user_id": "user_priya_patel_005",
            "title": "Owner & Clinical Director",
            "company": "Holistic Wellness Center",
            "bio": "Licensed physical therapist and wellness advocate. Built a comprehensive wellness center offering PT, massage therapy, and nutritional counseling. Focused on preventive care and community health education.",
            "location": "Phoenix, Arizona",
            "timezone": "America/Phoenix",
            "years_of_experience": 11.0,
            "hourly_rate": 140.0,
            "skills": [
                "Physical Therapy",
                "Healthcare Management",
                "Patient Care",
                "Insurance Billing",
                "Staff Management",
                "Community Outreach",
                "Health Education",
                "Regulatory Compliance",
                "Business Development",
                "Customer Service"
            ],
            "expertise_areas": [
                "Healthcare",
                "Physical Therapy",
                "Wellness",
                "Healthcare Management",
                "Community Health",
                "Preventive Care"
            ],
            "industries": [
                "Healthcare",
                "Wellness",
                "Physical Therapy",
                "Community Services"
            ],
            "linkedin_url": "https://linkedin.com/in/priya-patel-pt",
            "website_url": "https://holisticwellnesscenter.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # James Wilson - Professional Services
            "name": "James Wilson",
            "email": "james@wilsonaccounting.com",
            "username": "james_wilson",
            "clerk_user_id": "user_james_wilson_006",
            "title": "CPA & Managing Partner",
            "company": "Wilson & Associates CPA",
            "bio": "Certified Public Accountant with expertise in small business finance and tax planning. Founded a practice serving 200+ small businesses. Passionate about financial literacy and helping entrepreneurs succeed.",
            "location": "Denver, Colorado",
            "timezone": "America/Denver",
            "years_of_experience": 18.0,
            "hourly_rate": 165.0,
            "skills": [
                "Accounting",
                "Tax Planning",
                "Financial Analysis",
                "Business Consulting",
                "Audit & Compliance",
                "Financial Planning",
                "Budgeting",
                "Cash Flow Management",
                "Business Advisory",
                "Software Implementation"
            ],
            "expertise_areas": [
                "Accounting",
                "Tax Services",
                "Financial Planning",
                "Business Consulting",
                "Small Business Finance",
                "Compliance"
            ],
            "industries": [
                "Professional Services",
                "Accounting",
                "Financial Services",
                "Tax Services"
            ],
            "linkedin_url": "https://linkedin.com/in/james-wilson-cpa",
            "website_url": "https://wilsonaccounting.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Amanda Chen - E-commerce/Retail
            "name": "Amanda Chen",
            "email": "amanda@urbanstyle.com",
            "username": "amanda_chen",
            "clerk_user_id": "user_amanda_chen_007",
            "title": "Founder & Creative Director",
            "company": "Urban Style Boutique",
            "bio": "Fashion entrepreneur with background in design and retail. Started online boutique that grew to 3 physical locations. Expert in omnichannel retail, social media marketing, and customer experience design.",
            "location": "Seattle, Washington",
            "timezone": "America/Los_Angeles",
            "years_of_experience": 9.0,
            "hourly_rate": 135.0,
            "skills": [
                "Fashion Design",
                "Retail Management",
                "E-commerce",
                "Social Media Marketing",
                "Brand Development",
                "Customer Experience",
                "Inventory Management",
                "Visual Merchandising",
                "Trend Analysis",
                "Omnichannel Strategy"
            ],
            "expertise_areas": [
                "Fashion",
                "Retail",
                "E-commerce",
                "Brand Marketing",
                "Customer Experience",
                "Visual Design"
            ],
            "industries": [
                "Fashion",
                "Retail",
                "E-commerce",
                "Design"
            ],
            "linkedin_url": "https://linkedin.com/in/amanda-chen-fashion",
            "website_url": "https://urbanstyle.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Robert Martinez - Transportation/Logistics
            "name": "Robert Martinez",
            "email": "robert@fastlogistics.com",
            "username": "robert_martinez",
            "clerk_user_id": "user_robert_martinez_008",
            "title": "Owner & Operations Manager",
            "company": "Fast Track Logistics",
            "bio": "Former truck driver who built a regional logistics company. Specializes in last-mile delivery and supply chain optimization. Advocate for driver rights and sustainable transportation practices.",
            "location": "Houston, Texas",
            "timezone": "America/Chicago",
            "years_of_experience": 14.0,
            "hourly_rate": 120.0,
            "skills": [
                "Logistics Management",
                "Fleet Management",
                "Supply Chain",
                "Route Optimization",
                "Driver Management",
                "Safety Compliance",
                "Customer Service",
                "Warehousing",
                "Transportation Planning",
                "Cost Control"
            ],
            "expertise_areas": [
                "Transportation",
                "Logistics",
                "Supply Chain",
                "Fleet Management",
                "Operations",
                "Safety"
            ],
            "industries": [
                "Transportation",
                "Logistics",
                "Supply Chain",
                "Warehousing"
            ],
            "linkedin_url": "https://linkedin.com/in/robert-martinez-logistics",
            "website_url": "https://fastlogistics.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Lisa Brown - Education/Training
            "name": "Lisa Brown",
            "email": "lisa@skillsacademy.com",
            "username": "lisa_brown",
            "clerk_user_id": "user_lisa_brown_009",
            "title": "Director & Lead Instructor",
            "company": "Professional Skills Academy",
            "bio": "Former corporate trainer turned education entrepreneur. Developed comprehensive professional development programs for adults. Specializes in career transition support and workplace skills training.",
            "location": "Charlotte, North Carolina",
            "timezone": "America/New_York",
            "years_of_experience": 13.0,
            "hourly_rate": 145.0,
            "skills": [
                "Curriculum Development",
                "Adult Education",
                "Training Design",
                "Career Counseling",
                "Program Management",
                "Student Assessment",
                "Business Development",
                "Community Partnerships",
                "Grant Writing",
                "Educational Technology"
            ],
            "expertise_areas": [
                "Education",
                "Training",
                "Career Development",
                "Adult Learning",
                "Workforce Development",
                "Professional Development"
            ],
            "industries": [
                "Education",
                "Training",
                "Professional Development",
                "Human Resources"
            ],
            "linkedin_url": "https://linkedin.com/in/lisa-brown-educator",
            "website_url": "https://skillsacademy.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Michael O'Connor - Agriculture/Food Production
            "name": "Michael O'Connor",
            "email": "michael@greenfarm.com",
            "username": "michael_oconnor",
            "clerk_user_id": "user_michael_oconnor_010",
            "title": "Owner & Farm Manager",
            "company": "Green Valley Organic Farm",
            "bio": "Second-generation farmer who transitioned family farm to organic production. Supplies restaurants and farmers markets with premium organic produce. Leader in sustainable farming practices and agricultural education.",
            "location": "Fresno, California",
            "timezone": "America/Los_Angeles",
            "years_of_experience": 16.0,
            "hourly_rate": 110.0,
            "skills": [
                "Organic Farming",
                "Crop Management",
                "Soil Science",
                "Sustainable Agriculture",
                "Farm Equipment",
                "Irrigation Systems",
                "Pest Management",
                "Harvest Planning",
                "Market Sales",
                "Agricultural Finance"
            ],
            "expertise_areas": [
                "Agriculture",
                "Organic Farming",
                "Sustainability",
                "Food Production",
                "Farm Management",
                "Environmental Science"
            ],
            "industries": [
                "Agriculture",
                "Food Production",
                "Organic Farming",
                "Sustainability"
            ],
            "linkedin_url": "https://linkedin.com/in/michael-oconnor-farm",
            "website_url": "https://greenfarm.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Jennifer Lee - Beauty/Personal Care
            "name": "Jennifer Lee",
            "email": "jennifer@beautyspa.com",
            "username": "jennifer_lee",
            "clerk_user_id": "user_jennifer_lee_011",
            "title": "Owner & Lead Aesthetician",
            "company": "Radiant Beauty Spa",
            "bio": "Licensed aesthetician and spa owner with expertise in skincare and beauty treatments. Built a luxury spa serving high-end clientele. Passionate about natural beauty products and wellness-focused treatments.",
            "location": "Miami, Florida",
            "timezone": "America/New_York",
            "years_of_experience": 10.0,
            "hourly_rate": 130.0,
            "skills": [
                "Skincare",
                "Aesthetic Treatments",
                "Spa Management",
                "Product Knowledge",
                "Customer Service",
                "Staff Training",
                "Appointment Scheduling",
                "Retail Sales",
                "Sanitation Protocols",
                "Beauty Consulting"
            ],
            "expertise_areas": [
                "Beauty",
                "Skincare",
                "Spa Services",
                "Aesthetic Treatments",
                "Wellness",
                "Customer Service"
            ],
            "industries": [
                "Beauty",
                "Personal Care",
                "Wellness",
                "Spa Services"
            ],
            "linkedin_url": "https://linkedin.com/in/jennifer-lee-beauty",
            "website_url": "https://beautyspa.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Kevin Williams - Financial Services
            "name": "Kevin Williams",
            "email": "kevin@wealthadvisors.com",
            "username": "kevin_williams",
            "clerk_user_id": "user_kevin_williams_012",
            "title": "Principal & Financial Advisor",
            "company": "Williams Wealth Advisors",
            "bio": "Certified Financial Planner helping families and small businesses achieve financial security. Specializes in retirement planning, insurance, and investment strategies. Committed to financial education and community outreach.",
            "location": "Kansas City, Missouri",
            "timezone": "America/Chicago",
            "years_of_experience": 17.0,
            "hourly_rate": 180.0,
            "skills": [
                "Financial Planning",
                "Investment Management",
                "Retirement Planning",
                "Insurance Planning",
                "Estate Planning",
                "Tax Strategies",
                "Risk Assessment",
                "Portfolio Management",
                "Client Relations",
                "Regulatory Compliance"
            ],
            "expertise_areas": [
                "Financial Planning",
                "Wealth Management",
                "Insurance",
                "Investment Strategy",
                "Retirement Planning",
                "Estate Planning"
            ],
            "industries": [
                "Financial Services",
                "Insurance",
                "Investment Management",
                "Wealth Management"
            ],
            "linkedin_url": "https://linkedin.com/in/kevin-williams-cfp",
            "website_url": "https://wealthadvisors.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Maria Garcia - Marketing/Advertising
            "name": "Maria Garcia",
            "email": "maria@creativemark.com",
            "username": "maria_garcia",
            "clerk_user_id": "user_maria_garcia_013",
            "title": "Creative Director & Owner",
            "company": "Creative Marketing Solutions",
            "bio": "Bilingual marketing professional specializing in multicultural marketing campaigns. Built agency serving Hispanic and mainstream markets. Expert in digital marketing, brand strategy, and cultural adaptation.",
            "location": "San Antonio, Texas",
            "timezone": "America/Chicago",
            "years_of_experience": 12.0,
            "hourly_rate": 155.0,
            "skills": [
                "Digital Marketing",
                "Brand Strategy",
                "Content Creation",
                "Social Media Marketing",
                "SEO/SEM",
                "Multicultural Marketing",
                "Campaign Management",
                "Graphic Design",
                "Market Research",
                "Client Relations"
            ],
            "expertise_areas": [
                "Marketing",
                "Advertising",
                "Brand Strategy",
                "Digital Marketing",
                "Multicultural Marketing",
                "Creative Direction"
            ],
            "industries": [
                "Marketing",
                "Advertising",
                "Digital Media",
                "Creative Services"
            ],
            "linkedin_url": "https://linkedin.com/in/maria-garcia-marketing",
            "website_url": "https://creativemark.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Thomas Anderson - Automotive
            "name": "Thomas Anderson",
            "email": "thomas@autorepair.com",
            "username": "thomas_anderson",
            "clerk_user_id": "user_thomas_anderson_014",
            "title": "Owner & Master Mechanic",
            "company": "Anderson Auto Repair",
            "bio": "ASE-certified master mechanic with 22 years experience. Built reputation for honest, quality automotive service. Specializes in both foreign and domestic vehicles with focus on customer education and fair pricing.",
            "location": "Columbus, Ohio",
            "timezone": "America/New_York",
            "years_of_experience": 22.0,
            "hourly_rate": 115.0,
            "skills": [
                "Automotive Repair",
                "Diagnostic Services",
                "Engine Repair",
                "Brake Systems",
                "Electrical Systems",
                "Customer Service",
                "Shop Management",
                "Inventory Management",
                "Quality Control",
                "Safety Compliance"
            ],
            "expertise_areas": [
                "Automotive",
                "Mechanical Repair",
                "Diagnostic Services",
                "Shop Management",
                "Customer Service",
                "Quality Assurance"
            ],
            "industries": [
                "Automotive",
                "Repair Services",
                "Mechanical Services",
                "Transportation"
            ],
            "linkedin_url": "https://linkedin.com/in/thomas-anderson-auto",
            "website_url": "https://autorepair.com",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        },
        
        {
            # Rachel Johnson - Non-profit/Social Services
            "name": "Rachel Johnson",
            "email": "rachel@communityhelp.org",
            "username": "rachel_johnson",
            "clerk_user_id": "user_rachel_johnson_015",
            "title": "Executive Director",
            "company": "Community Empowerment Center",
            "bio": "Social worker turned non-profit executive. Founded organization providing job training and support services for underserved communities. Passionate about social justice and economic empowerment.",
            "location": "Detroit, Michigan",
            "timezone": "America/New_York",
            "years_of_experience": 19.0,
            "hourly_rate": 95.0,
            "skills": [
                "Non-profit Management",
                "Program Development",
                "Grant Writing",
                "Community Outreach",
                "Social Services",
                "Volunteer Management",
                "Fundraising",
                "Board Relations",
                "Strategic Planning",
                "Impact Measurement"
            ],
            "expertise_areas": [
                "Non-profit Management",
                "Social Services",
                "Community Development",
                "Program Management",
                "Grant Writing",
                "Social Justice"
            ],
            "industries": [
                "Non-profit",
                "Social Services",
                "Community Development",
                "Education"
            ],
            "linkedin_url": "https://linkedin.com/in/rachel-johnson-nonprofit",
            "website_url": "https://communityhelp.org",
            "is_active": True,
            "is_verified": True,
            "is_available": True,
            "profile_completed": True
        }
    ]
    
    # Add some additional fields and randomize some values
    for i, member in enumerate(members):
        # Add avatar URLs (fictional)
        member["avatar_url"] = f"https://api.dicebear.com/7.x/personas/svg?seed={member['username']}"
        
        # Randomize last active time within last 30 days
        days_ago = random.randint(0, 30)
        member["last_active_at"] = datetime.utcnow() - timedelta(days=days_ago)
        
        # Add some portfolio URLs for relevant members
        if member["company"] and member["website_url"]:
            member["portfolio_urls"] = [
                f"{member['website_url']}/portfolio",
                f"{member['website_url']}/case-studies"
            ]
        else:
            member["portfolio_urls"] = []
        
        # Add some extra metadata
        member["extra_metadata"] = {
            "onboarding_completed": True,
            "profile_views": random.randint(50, 500),
            "connection_count": random.randint(10, 200),
            "preferred_communication": random.choice(["email", "phone", "video"]),
            "business_stage": random.choice(["startup", "growth", "established", "scaling"]),
            "seeking_support": random.choice([
                "Funding", "Mentorship", "Partnerships", "Market Expansion", 
                "Operational Efficiency", "Technology Adoption"
            ])
        }
    
    return members


def get_sample_member_count() -> int:
    """Get the total number of sample members."""
    return len(generate_member_profiles())


def get_member_by_email(email: str) -> Dict[str, Any]:
    """Get a specific member by email address."""
    members = generate_member_profiles()
    for member in members:
        if member["email"] == email:
            return member
    raise ValueError(f"No member found with email: {email}")


def get_members_by_industry(industry: str) -> List[Dict[str, Any]]:
    """Get all members in a specific industry."""
    members = generate_member_profiles()
    return [
        member for member in members 
        if industry.lower() in [ind.lower() for ind in member["industries"]]
    ]


def get_members_by_expertise(expertise: str) -> List[Dict[str, Any]]:
    """Get all members with specific expertise."""
    members = generate_member_profiles()
    return [
        member for member in members 
        if expertise.lower() in [exp.lower() for exp in member["expertise_areas"]]
    ]


if __name__ == "__main__":
    # Quick test to validate the data
    members = generate_member_profiles()
    print(f"Generated {len(members)} member profiles")
    
    # Print summary
    industries = set()
    for member in members:
        industries.update(member["industries"])
    
    print(f"Industries covered: {sorted(industries)}")
    print(f"Sample member: {members[0]['name']} - {members[0]['title']}")