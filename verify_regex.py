
import re

title = "Crystal structure of Elongation Factor 4 (EF-4/LepA) in complex with GDPCP"
search_query = title

# This mocks the NEW backend logic
search_escaped = re.escape(search_query)
print(f"Escaped query: {search_escaped}")

match = re.search(search_escaped, title, re.IGNORECASE)
print(f"Match found? {bool(match)}")
