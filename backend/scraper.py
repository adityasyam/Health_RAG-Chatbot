#SCRAPER, CAN BE EXECUTED WITH ANY URL AND MARKDOWN SAVE PATH IN TERMINAL

import requests
from bs4 import BeautifulSoup
import sys
import os
import logging
#setting up logging to provide execution process info
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
#list of phrases to exclude from extracted content
EXCLUDE_PHRASES = ["read more", "follow us on social media", "share this article"]
#function to fetch html content of given URL
def get_html_file(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        response.encoding = response.apparent_encoding  
        logging.info(f"Successfully fetched content from {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch the URL: {e}")
        sys.exit(1)
#function to clean and extract relevant HTML content
def clean_html_file(content, url):
    soup = BeautifulSoup(content, "html.parser")

    def is_irrelevant_section(tag):
        irrelevant_classes = [
            "featured", "sidebar", "related", "sponsored", "promo", "navigation", "footer", "header",
            "menu", "social", "ad", "aside", "modal"
        ]
        if tag.has_attr('class'):
            return any(cls in tag['class'] for cls in irrelevant_classes)
        return False

    for script in soup(["script", "style", "noscript", "footer", "header", "aside", "nav", "menu"]):
        script.extract()

    for div in soup.find_all(['div', 'section']):
        if is_irrelevant_section(div):
            div.decompose()

    markdown_lines = []
    #adding source URL and title to the markdown
    markdown_lines.append(f"**Source URL**: {url}\n")
    if soup.title:
        markdown_lines.append(f"# {soup.title.get_text(strip=True)}")
    else:
        markdown_lines.append("# No Title")
    #adding meta description if available
    if soup.find("meta", {"name": "description"}):
        description = soup.find("meta", {"name": "description"}).get("content", "").strip()
        markdown_lines.append(f"**Description**: {description}\n")

    main_content_started = False
    #checking if text contains excluded phrases
    def contains_exclude_phrases(text):
        return any(phrase.lower() in text.lower() for phrase in EXCLUDE_PHRASES)
    #extracting and cleaning relevant content
    for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol', 'li']):
        text = tag.get_text(strip=True)
        
        if contains_exclude_phrases(text):
            continue
        #collecting main content after detecting relevant headers or paragraphs
        if not main_content_started and (tag.name in ['h1', 'h2'] or tag.name == 'p' and len(text) > 50):
            main_content_started = True
        
        if main_content_started:
            if tag.name.startswith("h"):
                level = int(tag.name[1])
                markdown_lines.append("#" * level + " " + text)
            elif tag.name == 'p':
                markdown_lines.append(text)
            elif tag.name == 'li':
                markdown_lines.append(f"* {text}")

    return "\n\n".join(markdown_lines)
#scraping article and saving as markdown file
def scrape_article_to_markdown(url, save_path):
    html_content = get_html_file(url)
    markdown_text = clean_html_file(html_content, url)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    try:
        with open(save_path, "w", encoding="utf-8") as output_file:
            output_file.write(markdown_text)
        logging.info(f"Markdown file saved at {save_path}")
    except Exception as e:
        logging.error(f"Failed to save markdown file: {e}")
        sys.exit(1)


# if __name__ == "__main__":
#     from urls import urls

#     for url in urls:
#         save_path = f"saved_markdown/{url.split('/')[-1]}.md"
#         scrape_article_to_markdown(url, save_path)

#main method to loop over all healthline urls and convert to markdown
if __name__ == "__main__":
    from healthline_urls import healthline_urls

    for url in healthline_urls:
        save_path = f"healthline_markdwns_complete/{url.split('/')[-1]}.md"
        scrape_article_to_markdown(url, save_path)

