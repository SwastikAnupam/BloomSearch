import requests
import json
import csv
import xml.etree.ElementTree as ET
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
import re

class SpiderSearch:
    def __init__(self, start_urls, max_depth=3, max_threads=5):
        self.start_urls = start_urls if isinstance(start_urls, list) else [start_urls]
        self.max_depth = max_depth
        self.max_threads = max_threads
        self.visited = set()
        self.data = []

    def crawl(self, url, depth=0):
        if depth > self.max_depth or url in self.visited:
            return

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except (RequestException, Timeout, ConnectionError, HTTPError) as e:
            print(f"Error crawling {url}: {e}")
            return

        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' in content_type:
            parser = 'html.parser'
            page_data = self.process_html(url, BeautifulSoup(response.text, parser))
        elif 'json' in content_type:
            parser = 'json'
            page_data = self.process_json(url, response.text)
        elif 'xml' in content_type:
            parser = 'lxml'
            root = ET.fromstring(response.content)
            page_data = self.process_xml(url, root)
        elif 'rss' in content_type:
            parser = 'feedparser'
            page_data = self.process_rss(url, response.text)
        elif 'csv' in content_type:
            parser = 'csv'
            page_data = self.process_csv(url, response.text)
        else:
            parser = 'unknown'
            page_data = {'Parser': parser, 'URL': url}

        self.data.append(page_data)
        self.visited.add(url)

        for link in self.extract_links(response.text):
            next_url = urljoin(url, link)
            self.crawl(next_url, depth + 1)

    def process_html(self, url, soup):
        # Implement HTML-specific processing here
        title = soup.title.string if soup.title else 'No Title'
        return {'Parser': 'HTML', 'Title': title, 'URL': url}

    def process_json(self, url, json_content):
        # Implement JSON-specific processing here
        data = json.loads(json_content)
        return {'Parser': 'JSON', 'Data': data, 'URL': url}

    def process_xml(self, url, root):
        # Implement XML-specific processing here
        # For example, extract data from an XML document
        return {'Parser': 'XML', 'URL': url}

    def process_rss(self, url, rss_content):
        # Implement RSS-specific processing here
        feed = feedparser.parse(rss_content)
        entries = [{'Title': entry.title, 'Link': entry.link} for entry in feed.entries]
        return {'Parser': 'RSS', 'Entries': entries, 'URL': url}

    def process_csv(self, url, csv_content):
        # Implement CSV-specific processing here
        reader = csv.DictReader(csv_content.splitlines())
        data = [row for row in reader]
        return {'Parser': 'CSV', 'Data': data, 'URL': url}

    def extract_links(self, html_content):
        # Extract links from HTML content
        # Customize this method for specific link extraction logic
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            links.append(link['href'])
        return links

    def save_to_csv(self, filename):
        # Save the collected data to a CSV file
        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['Parser', 'Title', 'Data', 'Entries', 'URL']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for page_data in self.data:
                writer.writerow(page_data)

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            for start_url in self.start_urls:
                executor.submit(self.crawl, start_url)

if __name__ == "__main__":
    start_urls = ["https://www.bbc.com/news"]  # Enter URLs to start searching websites linked
    spider = SpiderSearch(start_urls, max_depth=3, max_threads=10)
    spider.run()
    spider.save_to_csv("web_data.csv")
