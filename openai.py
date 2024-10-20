# If you use openAI:  you will need to go to openAI Playground and get a token

# 1.  write the .env file to your directory so you can load the key

%%writefile .env
OPENAI_API_KEY="my_secret_key"


# 2. insteall these packages
!pip install -q python-dotenv
!pip install -q prompts
!pip install -q openai

# 3. import openai
import openai

# 4. load your environment
import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# 5. Load the model:
    
# load the gpt-4o model
model = 'gpt-4o'    

# 6. below is a function to generate the opneAI response

import re
import json

temperature = 0.0
max_tokens = 4096  # Increased max_tokens to accommodate more output
top_p = 0.95
frequency_penalty = 1.2
presence_penalty = 1.2

def generate_openai_response(instruction, review):
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": review}
    ]

    completion = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        #stop=["\n\n"]  # Ensures proper end after JSON block
        stop=["}"]  # Stop generation once the JSON object is completed
    )

    # Strip off any unwanted characters and try parsing the JSON
    output = completion.choices[0].message.content.strip()

    # Attempt to close the JSON if it's incomplete
    if not output.endswith("}"):
        output += "}"

    # Fix missing quotes around keys
    output = re.sub(r'(?<!")(\b\d+\b)(?=:)', r'"\1"', output)  # Adds quotes around unquoted numbers

    # Fix missing quotes around values (non-numeric values)
    output = re.sub(r'(?<=: )([A-Za-z0-9_,\.\'\s-]+)(?=,|})', r'"\1"', output)


    # Fix any trailing commas before the closing brace
    if output.endswith(",}"):
        output = output[:-2] + "}"  # Remove the trailing comma and add the closing brace

    # Fix missing double quotes around values in object-like structures
    output = re.sub(r'(?<=: {)([^}]+)(?=})', r'"\1"', output)  # This fixes values inside {} without quotes

    # Replace curly quotes with straight quotes
    output = output.replace('“', '"').replace('”', '"')

# 7. Define the function to use the above function to get categories 

def get_categories(news):

    news_segments = news.split('||')
    summary = {} # initializing empty dictionary

    for i, segment in enumerate(news_segments):
        if segment.strip():  # Only process non-empty segments
            segment_summary = generate_openai_response(instructions, segment.strip()) # calls our generate function to get json output for the segment
            summary[i + 1] = segment_summary #populates the dictionary with key/values


    combined_topics = set()  # Using a set to keep unique values

    for key, json_str in summary.items():
        # Load the JSON string into a dictionary
        topics_dict = json.loads(json_str)

        # Add all the values (topics) to the set to ensure uniqueness
        combined_topics.update(topics_dict.values())

        # Create a single JSON output with unique values, assign each unique value a key
        unique_topics_dict = {i + 1: topic for i, topic in enumerate(sorted(combined_topics))}

    # Convert the dictionary to a JSON string
    unique_topics_json = json.dumps(unique_topics_dict)
    return unique_topics_json


# 8. Test with 1 news article

news = data_1.loc[17, 'News']
get_categories(news)

# Output:
# '{"1": "Business", "2": "Economy", "3": "Finance", "4": "Investment", "5": "Manufacturing", "6": "Media", "7": "Politics", "8": "Taxation", "9": "Technology", "10": "Trade"}'    



