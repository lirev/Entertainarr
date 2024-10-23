from datetime import date, timedelta
import re
today = date.today()
yesterday = today - timedelta(days=1)

print(yesterday)



# Input string
text = 'News off the TopMONDAY OCTOBER 21, 2024'

# Regular expression to extract text before the date pattern
match = re.match(r'^(.*?)(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)', text, re.IGNORECASE)

# Extract the title part
if match:
    title = match.group(1).strip()  # Extract and remove any trailing spaces
    print(f'Title: {title}')
else:
    print('No title found.')