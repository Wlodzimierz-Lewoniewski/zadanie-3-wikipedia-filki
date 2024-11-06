import requests
from bs4 import BeautifulSoup

def search():
    wiki_name = input("Enter Wikipedia category name: ")
    url = "https://pl.wikipedia.org/wiki/Kategoria:" + wiki_name.replace(' ', '_')
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    pages = soup.find("div", id="mw-pages")

    if not pages:
        print("No pages")
        return

    articles = [{"url": link["href"], "name": link["title"]} for link in pages.find_all("a") if "title" in link.attrs]

    for idx in range(2):
        if idx >= len(articles):
            print(f"Article {idx + 1}: Information not found")
            continue

        article = articles[idx]
        full_url = "https://pl.wikipedia.org" + article["url"]
        article_response = requests.get(full_url)
        article_soup = BeautifulSoup(article_response.text, "html.parser")

        content = article_soup.find('div', {'id': 'mw-content-text', 'class': 'mw-body-content'})
        titles = []
        if content:
            anchor_tags = content.select('a:not(.extiw)')
            titles = [anchor.get('title') for anchor in anchor_tags if anchor.get('title') and anchor.get_text(strip=True)][:5]

        content_text_div = article_soup.find("div", {"class": "mw-content-ltr mw-parser-output"})
        image_tags = content_text_div.find_all("img", src=True) if content_text_div else []
        image_urls = [img["src"] for img in image_tags[:3]]

        refer = article_soup.find("ol", {"class": "references"})
        reference_urls = [link.get('href') for link in refer.find_all('a', class_='external text') if link.get('href')] if refer else []

        refer_div = article_soup.find_all("li", {"id": lambda x: x and x.startswith("cite")})
        for ref in refer_div:
            link = ref.find('a', class_='external text')
            if link and link.get('href'):
                reference_urls.append(link.get('href'))

        reference_urls = [url.replace("&", "&amp;") for url in dict.fromkeys(reference_urls)][:3]

        cat = article_soup.find("div", {"id": "mw-normal-catlinks"})
        cat_names = [a.get_text() for a in cat.find_all("a")[1:4]] if cat else []

        print(" | ".join(titles))
        print(" | ".join(image_urls))
        print(" | ".join(reference_urls))
        print(" | ".join(cat_names))

if __name__ == "__main__":
    search()
