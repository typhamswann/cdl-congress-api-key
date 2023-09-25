import requests
from xml.etree import ElementTree as ET
import json
from bs4 import BeautifulSoup
import csv
import pandas as pd

API_BASE_URL = "https://api.congress.gov/v3/daily-congressional-record"
API_KEY = [YOUR KEY]

def get_congressional_speeches_api(audit_mode=True):
    volumes_url = f"{API_BASE_URL}?api_key={API_KEY}"
    response = requests.get(volumes_url)
    data = json.loads(response.content)
    
    speeches = []

    for daily_record in data['dailyCongressionalRecord']:
        volume_number = daily_record['volumeNumber']
        issue_number = daily_record['issueNumber']
        
        articles_url = f"{API_BASE_URL}/{volume_number}/{issue_number}/articles?api_key={API_KEY}"
        articles_response = requests.get(articles_url)
        articles_data = json.loads(articles_response.content)
        speeches.extend(get_congressional_speeches(articles_data))
        
    return speeches

def get_congressional_speeches(articles_data, audit_mode=True):
    speeches_dict = {}
    
    for section in articles_data['articles']:
        for article in section['sectionArticles']:
            title = article['title']
            for text_block in article['text']:
                url = text_block['url']
                if url.endswith('.htm'):
                    speeches_dict[url] = title
    
    speeches = [{'title': title, 'url': url} for url, title in speeches_dict.items()]
    return speeches

def extract_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"An error occurred: {e}"

    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.get_text())
    return soup.get_text()

def save_to_csv(speeches):
    data = []
    for speech in speeches:
        speech_content = extract_text(speech['url'])
        data.append({'title': speech['title'], 'content': speech_content})
    df = pd.DataFrame(data)
    df.to_csv('speeches.csv', index=False, quoting=1, escapechar='\\')  # Added escapechar argument


if __name__ == "__main__":
    speeches = get_congressional_speeches_api()
    save_to_csv(speeches)
