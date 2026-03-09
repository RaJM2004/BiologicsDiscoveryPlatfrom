
import re

# Simulate the backend logic
# PDB Title example
title = "Crystal structure of Elongation Factor 4 (EF-4/LepA) in complex with GDPCP"
search_query = title  # The frontend sends the full title as search query

# Backend logic: {"name": {"$regex": search, "$options": "i"}}
# In python re:
pattern = search_query
match = re.search(pattern, title, re.IGNORECASE)

print(f"Title: {title}")
print(f"Search: {search_query}")
print(f"Match found? {bool(match)}")

# Let's try to understand why it fails
# The '(' in pattern starts a group. It does NOT match a literal '('.
# The title has a literal '('.
# So pattern expects [Start Group]EF-4... but text has '('. Mismatch.

print("-" * 20)
print("Demonstrating mismatch:")
try:
    # If we escape the search query
    escaped_query = re.escape(search_query)
    match_escaped = re.search(escaped_query, title, re.IGNORECASE)
    print(f"Escaped Search: {escaped_query}")
    print(f"Match found with escape? {bool(match_escaped)}")
except Exception as e:
    print(e)
