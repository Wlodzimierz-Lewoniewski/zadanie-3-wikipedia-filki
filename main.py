import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def get_category_articles(soup):
    pages_div = soup.find("div", id="mw-pages")
    if not pages_div:
        print("No pages found in this category.")
        return []
    
    articles = [
        {"url": "https://pl.wikipedia.org" + link["href"], "name": link["title"]}
        for link in pages_div.find_all("a") if "title" in link.attrs
    ]
    return articles[:2]  

def extract_internal_titles(content_div):
    titles = []
    if content_div:
        links = content_div.select('a:not(.extiw)')
        titles = [
            link.get('title') for link in links 
            if link.get('title') and link.get_text(strip=True)
        ][:5]
    return titles

def extract_image_urls(content_div):
    if not content_div:
        return []
    
    images = content_div.find_all("img", src=True)
    return [img["src"] for img in images[:3]]

def extract_references(soup):
    reference_urls = set()
    
    references_section = soup.find("ol", {"class": "references"})
    if references_section:
        links = references_section.find_all('a', class_='external text')
        reference_urls.update(link.get('href') for link in links if link.get('href'))

    citation_refs = soup.find_all("li", {"id": lambda x: x and x.startswith("cite")})
    for ref in citation_refs:
        link = ref.find('a', class_='external text')
        if link and link.get('href'):
            reference_urls.add(link.get('href'))
    
    return [url.replace("&", "&amp;") for url in list(reference_urls)[:3]]

def extract_categories(soup):
    categories_div = soup.find("div", {"id": "mw-normal-catlinks"})
    if not categories_div:
        return []
    
    category_links = categories_div.find_all("a")[1:4]  
    return [link.get_text() for link in category_links]

def process_article(article):
    """Fetch and extract data from an individual article."""
    article_html = fetch_html(article["url"])
    article_soup = BeautifulSoup(article_html, "html.parser")

    content_div = article_soup.find("div", {'id': 'mw-content-text', 'class': 'mw-body-content'})
    titles = extract_internal_titles(content_div)
    images = extract_image_urls(content_div)
    references = extract_references(article_soup)
    categories = extract_categories(article_soup)

    print(" | ".join(titles))
    print(" | ".join(images))
    print(" | ".join(references))
    print(" | ".join(categories))
    print()  

def search():
    wiki_name = input("Enter Wikipedia category name: ")
    url = "https://pl.wikipedia.org/wiki/Kategoria:" + wiki_name.replace(' ', '_')
    
    category_html = fetch_html(url)
    soup = BeautifulSoup(category_html, "html.parser")
    
    articles = get_category_articles(soup)
    if not articles:
        return

    for idx, article in enumerate(articles):
        print(f"\nProcessing article {idx + 1}: {article['name']}")
        process_article(article)

if __name__ == "__main__":
    search()
