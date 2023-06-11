import pandas as pd
from langdetect import detect

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('tracks.csv')
i = 1

# Function to detect the language of a given text
def detect_language(text):
    global i
    print(i)
    i += 1
    try:
        return detect(text)
    except:
        return 'unknown'
# Apply language detection to the 'name' column and create a new 'language' column
df['language'] = df['name'].apply(detect_language)

# Save the modified DataFrame back to a CSV file
df.to_csv('tracks_with_language.csv', index=False)
