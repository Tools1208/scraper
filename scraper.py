import re
import time
import random
import json
import csv
import os
import argparse
from datetime import datetime
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests

# Configuration
OUTPUT_DIR = "output"
DELAY = (1, 3)  # Random delay between requests (seconds)
MAX_RETRIES = 3
TIMEOUT = 10  # Request timeout in seconds
HEADERS = {
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.google.com/'
}

class Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.session.headers.update(HEADERS)
        self.create_output_dir()

    def create_output_dir(self):
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    def get_random_user_agent(self):
        try:
            return self.ua.random
        except:
            # Fallback user agents
            return random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36 Edg/89.0.774.57'
            ])

    def scrape(self, url, retries=0):
        try:
            # Rate limiting
            time.sleep(random.uniform(*DELAY))
            
            # Update headers with new user agent
            self.session.headers.update({'User-Agent': self.get_random_user_agent()})
            
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Sophisticated parsing
            data = {
                'url': url,
                'emails': self.extract_emails(soup),
                'phones': self.extract_phones(soup),
                'social_media': self.extract_social_media(soup),
                'metadata': self.extract_metadata(soup),
                'timestamp': datetime.now().isoformat()
            }
            
            return data
            
        except requests.exceptions.RequestException as e:
            if retries < MAX_RETRIES:
                print(f"Retrying ({retries+1}/{MAX_RETRIES})...")
                time.sleep(2**retries)  # Exponential backoff
                return self.scrape(url, retries+1)
            else:
                self.log_error(f"Failed to retrieve {url}: {str(e)}")
                return None

    def extract_emails(self, soup):
        email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        emails = set(email_pattern.findall(soup.get_text()))
        
        # Check mailto links
        for link in soup.find_all('a', href=True):
            if link['href'].startswith('mailto:'):
                emails.add(link['href'][7:])
                
        return list(emails)

    def extract_phones(self, soup):
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(\d{2,4}\)\s?\d{3,4}[-.\s]?\d{4}',
            r'\d{3}-\d{3}-\d{4}',
            r'\d{3}\.\d{3}\.\d{4}',
        ]
        
        phones = set()
        for pattern in phone_patterns:
            phones.update(re.findall(pattern, soup.get_text()))
            
        return list(phones)

    def extract_social_media(self, soup):
        social_platforms = ['facebook', 'twitter', 'linkedin', 'instagram']
        social_links = []
        
        for link in soup.find_all('a', href=True):
            for platform in social_platforms:
                if platform in link['href'].lower():
                    social_links.append(link['href'])
                    
        return list(set(social_links))

    def extract_metadata(self, soup):
        metadata = {}
        for meta in soup.find_all('meta'):
            if 'name' in meta.attrs and 'content' in meta.attrs:
                metadata[meta['name'].lower()] = meta['content']
                
        return metadata

    def save_results(self, data, format='json'):
        filename = f"{OUTPUT_DIR}/scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if format == 'json':
            with open(f"{filename}.json", 'w') as f:
                json.dump(data, f, indent=4)
        elif format == 'csv':
            with open(f"{filename}.csv", 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Type', 'Value'])
                writer.writerows([('Email', email) for email in data['emails']])
                writer.writerows([('Phone', phone) for phone in data['phones']])
                writer.writerows([('Social', link) for link in data['social_media']])
        else:
            self.log_error("Invalid format specified")

    def log_error(self, message):
        with open('error_log.txt', 'a') as f:
            f.write(f"[{datetime.now()}] {message}\n")

def main():
    parser = argparse.ArgumentParser(description='Advanced Web Scraper')
    parser.add_argument('url', help='Target URL (authorized)')
    parser.add_argument('--format', choices=['json', 'csv'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('--delay', type=int, nargs=2, default=DELAY,
                        help='Request delay range (min max)')
    args = parser.parse_args()

    global DELAY
    DELAY = tuple(args.delay)
    
    scraper = Scraper()
    print(f"Scraping {args.url} with user-agent: {scraper.get_random_user_agent()}")
    
    data = scraper.scrape(args.url)
    if data:
        print(f"\nFound {len(data['emails'])} emails, {len(data['phones'])} phone numbers")
        print(f"Social media links: {len(data['social_media'])}")
        print(f"Metadata entries: {len(data['metadata'])}")
        
        scraper.save_results(data, args.format)
        print(f"Results saved in {args.format.upper()} format")

if __name__ == "__main__":
    main()
