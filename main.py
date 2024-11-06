import requests
from bs4 import BeautifulSoup
import re

def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_wikipedia_data(category_name):
    base_url = "https://pl.wikipedia.org/wiki/Kategoria:"
    category_url = base_url + category_name.replace(" ", "_")
    
    category_html = fetch_html(category_url)
    category_soup = BeautifulSoup(category_html, 'html.parser')
    

    article_links = []
    for link in category_soup.select("div.mw-category a")[:2]:  
        article_links.append("https://pl.wikipedia.org" + link['href'])
    
    results = []
    
    for article_url in article_links:
        article_html = fetch_html(article_url)
        article_soup = BeautifulSoup(article_html, 'html.parser')
        
        internal_links = []
        for link in article_soup.find_all("a", href=True, limit=5):
            if link['href'].startswith('/wiki/') and not any(ns in link['href'] for ns in [':', '/File:', '/Kategorie:', '/Szablon:']):
                internal_links.append(link.text)
            if len(internal_links) >= 5:
                break
        
        images = []
        for img in article_soup.find_all("img", src=True, limit=3):
            if "upload.wikimedia.org" in img['src']:
                images.append("https:" + img['src'])
        
        external_links = []
        for link in article_soup.find_all("a", href=True, limit=3):
            if link['href'].startswith("http") and "wikipedia.org" not in link['href']:
                external_links.append(link['href'])
        
        categories = []
        for cat in article_soup.select("div#mw-normal-catlinks ul li a", limit=3):
            categories.append(cat.text)
        
        article_result = []
        
        article_result.append(" | ".join(internal_links) if internal_links else "")
        article_result.append(" | ".join(images) if images else "")
        article_result.append(" | ".join(external_links) if external_links else "")
        article_result.append(" | ".join(categories) if categories else "")
        
        results.append("\n".join(article_result))
    
    return results
category_name = input().strip()
data = extract_wikipedia_data(category_name)

for idx, article_data in enumerate(data, start=1):
    print(article_data)
    if idx < len(data):  
        print()
