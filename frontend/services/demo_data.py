"""
Sample and Demo Dataset for MemoryBox
Provides rich, realistic memories across Family, Travel, College, Achievements, and Events
so judges and users can immediately explore all AI features with one click.
"""

from typing import List
from ..utils.types import MemoryItemView


def get_demo_memories() -> List[MemoryItemView]:
    """Returns a curated list of realistic demo memories for judging and onboarding."""
    return [
        MemoryItemView(
            id="demo_mem_1",
            title="Sankranti Harvest Festival at Ancestral Village",
            summary="Three generations gathered around the traditional brass pot to watch the sweet milk boil over under the clear January sun.",
            raw_text="Every Sankranti, we all travelled to our village home near Thanjavur. Grandfather would sit in the courtyard reciting Tamil blessings while Mother decorated the clay stove with turmeric and kumkum. When the milk bubbled over, all of us shouted 'Pongalo Pongal!' together. The aroma of jaggery, cardamom, and roasted cashews filled the morning breeze.",
            description="A deeply cherished family tradition where 14 relatives from across India reunited in the village courtyard for the annual harvest festival.",
            category="Family",
            tags=["Heritage", "Festival", "Traditions", "Harvest", "Grandparents"],
            date="January 14, 2026",
            year=2026,
            month="January",
            location="Thanjavur, Tamil Nadu",
            people=["Grandfather Sundaram", "Grandmother Meenakshi", "Uncle Arvind", "Aunt Priya", "Sister Divya"],
            image_url="https://images.unsplash.com/photo-1609137144822-771c77f0a6d0?auto=format&fit=crop&w=800&q=80",
            sentiment="Warm, Nostalgic & Reverent",
            why_it_matters="Preserves the timeless harvest ritual that binds three generations across rapid modern urbanization.",
            created_at="2026-01-15",
            is_demo=True
        ),
        MemoryItemView(
            id="demo_mem_2",
            title="Sunrise Trek to Chamundi Hills",
            summary="A misty dawn ascent of 1,000 stone steps overlooking the royal palace city of Mysore.",
            raw_text="We woke up at 4:30 AM before the city stirred. The stone steps were cool beneath our feet, carved centuries ago. Halfway up, a young monk offered us sweet holy water and bilva leaves. Reaching the summit just as the first amber rays kissed the Chamundeshwari temple gopuram is a moment forever etched into my mind.",
            description="An invigorating early morning hike taken during our annual summer holiday in Karnataka.",
            category="Travel",
            tags=["Trek", "Temples", "Sunrise", "Mysore", "Nature"],
            date="May 18, 2025",
            year=2025,
            month="May",
            location="Mysore, Karnataka",
            people=["Brother Rohit", "Cousin Sneha"],
            image_url="https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=800&q=80",
            sentiment="Exhilarating & Serene",
            why_it_matters="Marks the summer where we learned to slow down and find peace in silent ancestral landscapes.",
            created_at="2025-05-19",
            is_demo=True
        ),
        MemoryItemView(
            id="demo_mem_3",
            title="Final Year Engineering Project Showcase",
            summary="After 6 months of sleepless nights, our autonomous rover completed its obstacle course to roaring cheers from the department.",
            raw_text="The campus auditorium was packed. Our team was nervous because the motor driver had burned out at 2 AM the night before. When Karthik flicked the master switch and the rover successfully mapped the terrain and relayed the telemetry without a single glitch, Professor Raman stood up and clapped. We hugged each other in tears of sheer relief.",
            description="The crowning achievement of our four-year undergraduate engineering journey, proving that perseverance wins against impossible deadlines.",
            category="College",
            tags=["College", "Engineering", "Robotics", "Teamwork", "Graduation"],
            date="March 22, 2025",
            year=2025,
            month="March",
            location="Campus Auditorium, Bengaluru",
            people=["Karthik", "Rohan", "Ananya", "Prof. Raman"],
            image_url="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=800&q=80",
            sentiment="Triumphant & Proud",
            why_it_matters="Represents the transformative transition from young students into confident engineers.",
            created_at="2025-03-23",
            is_demo=True
        ),
        MemoryItemView(
            id="demo_mem_4",
            title="Winning the State AI Innovation Hackathon",
            summary="Awarded the Gold Trophy and seed grant for our privacy-first digital preservation platform.",
            raw_text="Over 48 hours of intense coding, coffee runs, and high-stakes pitching. The moment the jury announced 'First Place goes to MemoryBox', the entire room erupted. Presenting how AI can protect elder oral histories was honored by the Minister of Innovation.",
            description="Our first major technological recognition on a state-wide innovation stage.",
            category="Achievements",
            tags=["Hackathon", "AI", "First Place", "Innovation", "Milestone"],
            date="November 12, 2024",
            year=2024,
            month="November",
            location="Tech Convention Center, Hyderabad",
            people=["Divya", "Kalyan", "Jury Panel"],
            image_url="https://images.unsplash.com/photo-1578269174936-2709b6aeb913?auto=format&fit=crop&w=800&q=80",
            sentiment="Ecstatic & Inspiring",
            why_it_matters="Validated our vision that technology should serve human memory and empathy, not just engagement.",
            created_at="2024-11-13",
            is_demo=True
        ),
        MemoryItemView(
            id="demo_mem_5",
            title="Grandmother's 80th Golden Jubilee Birthday",
            summary="A musical evening filled with classical Carnatic veena, old family photographs, and handwritten letters from four continents.",
            raw_text="Grandmother wore her heavy maroon Kanjeevaram silk saree that her father bought in 1964. We surprised her with a leather-bound scrapbook compiled from 50 relatives living across India, Singapore, the UK, and the US. She spent two hours softly smiling at childhood pictures she thought had been lost forever.",
            description="A sacred familial milestone celebrating eight decades of resilience, love, and wisdom.",
            category="Events",
            tags=["Milestone", "Birthday", "Carnatic Music", "Family Reunion"],
            date="August 10, 2024",
            year=2024,
            month="August",
            location="Ancestral Residence, Chennai",
            people=["Grandmother Saraswathi", "Uncle Sridhar", "Entire Clan"],
            image_url="https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&w=800&q=80",
            sentiment="Sacred, Loving & Emotional",
            why_it_matters="A generational milestone where the family documented 80 years of living oral history.",
            created_at="2024-08-11",
            is_demo=True
        )
    ]
