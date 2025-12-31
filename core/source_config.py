#!/usr/bin/env python3
"""
Source configuration for optimized URL detection in Capcat.
"""

# Define the mapping of URL patterns to source identifiers
SOURCE_PATTERNS = {
    # Tech news sources (tech trio)
    "hn": ["news.ycombinator.com"],
    "lb": ["lobste.rs"],
    "iq": ["infoq.com"],
    # Additional sources from the research list
    "gn": ["ground.news"],
    "bbc": ["bbc.com"],
    "TechCrunch": ["techcrunch.com"],
    "wired": ["wired.com"],
    "TheVerge": ["theverge.com"],
    "engadget": ["engadget.com"],
    "gizmodo": ["gizmodo.com"],
    "mashable": ["mashable.com"],
    "recode": ["recode.net"],
    "venturebeat": ["venturebeat.com"],
    "cnet": ["cnet.com"],
    "cnn": ["cnn.com"],
    "reuters": ["reuters.com"],
    "aljazeera": ["aljazeera.com"],
    "guardian": ["theguardian.com"],
    "nytimes": ["nytimes.com"],
    "washingtonpost": ["washingtonpost.com"],
    "financialtimes": ["ft.com"],
    "bloomberg": ["bloomberg.com"],
    "ap": ["apnews.com"],
    "mittechreview": ["technologyreview.com"],
    "scientificamerican": ["scientificamerican.com"],
    "nature": ["nature.com"],
}

# Define source names for user-friendly messages
SOURCE_NAMES = {
    "hn": "Hacker News",
    "lb": "Lobsters",
    "iq": "InfoQ",
    "gn": "Ground News",
    "bbc": "BBC News",
    "techcrunch": "TechCrunch",
    "arstechnica": "Ars Technica",
    "wired": "Wired",
    "theverge": "The Verge",
    "engadget": "Engadget",
    "gizmodo": "Gizmodo",
    "mashable": "Mashable",
    "recode": "Recode",
    "venturebeat": "VentureBeat",
    "cnet": "CNET",
    "cnn": "CNN",
    "reuters": "Reuters",
    "aljazeera": "Al Jazeera",
    "guardian": "The Guardian",
    "nytimes": "The New York Times",
    "washingtonpost": "The Washington Post",
    "financialtimes": "Financial Times",
    "bloomberg": "Bloomberg",
    "ap": "Associated Press",
    "mittechreview": "MIT Technology Review",
    "scientificamerican": "Scientific American",
    "nature": "Nature",
    "science": "Science",
    "ted": "TED",
    "researchgate": "ResearchGate",
    "academia": "Academia.edu",
}


def detect_source(url):
    """
    Detect the source identifier for a given URL.

    Args:
        url (str): The URL to analyze

    Returns:
        str or None: The source identifier or None if not recognized
    """
    url_lower = url.lower()

    for source_id, patterns in SOURCE_PATTERNS.items():
        for pattern in patterns:
            if pattern in url_lower:
                return source_id

    return None
