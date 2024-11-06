import requests
import re
from urllib.parse import unquote

def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_category_links(html):

    link_pattern = r'href="(/wiki/[^":]+?)"[^>]*?>([^<]+)</a>'
    matches = re.findall(link_pattern, html)
    
    article_urls = [match[0] for match in matches if ':' not in match[0]][:2]
    article_titles = [match[1] for match in matches if ':' not in match[0]][:2]
    
    return article_urls, article_titles

def fetch_article_data(article_url):
    url = f"https://pl.wikipedia.org{article_url}"
    html = fetch_html(url)

    return {
        'internal_links': extract_internal_links(html),
        'images': extract_images(html),
        'sources': extract_sources(html),
        'categories': extract_categories(html)
    }

def extract_internal_links(html):

    link_pattern = r'href="(/wiki/[^":]+?)"[^>]*?title="([^"]+)"'
    matches = re.findall(link_pattern, html)

    internal_links = []
    for href, title in matches:
        if ':' not in href and title != "Ziemia" and "Zobacz stronę treści [c]" not in title:
            internal_links.append(title)
        if len(internal_links) == 5:
            break
    return internal_links

def extract_images(html):

    ignored_images = {
        '/static/images/icons/wikipedia.png',
        '//upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Geographylogo.svg/20px-Geographylogo.svg.png',
        '/static/images/footer/wikimedia-button.png',
        '/static/images/footer/poweredby_mediawiki_88x31.png'
    }
    
    image_pattern = r'src="([^"]+\.(?:jpg|jpeg|png|gif))"'
    images = re.findall(image_pattern, html)

    images = ["https:" + img if img.startswith("//") else img for img in images if img not in ignored_images][:3]
    return images

def extract_sources(html):

    ref_pattern = r'class="reference-text">.*?href="(http[^"]+)"'
    matches = re.findall(ref_pattern, html)

    sources = [url.replace('&', '&amp;') for url in matches][:3]
    return sources

def extract_categories(html):
   
    cat_pattern = r'id="mw-normal-catlinks".*?<ul>(.*?)</ul>'
    ul_content = re.search(cat_pattern, html, re.DOTALL)
 
    categories = []
    if ul_content:
        cat_link_pattern = r'href="[^"]+">([^<]+)</a>'
        categories = re.findall(cat_link_pattern, ul_content.group(1))[:3]
    
    return categories

def main():
    category_name = input("Enter category name: ")
    category_url = f"https://pl.wikipedia.org/wiki/Kategoria:{category_name.replace(' ', '_')}"
    category_html = fetch_html(category_url)

    article_urls, article_titles = extract_category_links(category_html)
    
    for url, title in zip(article_urls, article_titles):
        article_data = fetch_article_data(url)
        
        print(" | ".join(article_data['internal_links']))
        print(" | ".join(article_data['images']))
        print(" | ".join(article_data['sources']))
        print(" | ".join(article_data['categories']))
        print()  


main()
