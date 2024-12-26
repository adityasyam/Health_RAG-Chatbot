import requests
from bs4 import BeautifulSoup
import json
import os

#purpose: to fetch topics from url
def get_topics(retries=3):
    url = "https://www.healthline.com/directory/topics"
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, timeout=10) 
            if response.status_code == 200: 
                html_content = response.content
                break
            else:
                print(f"Couldn't retrieve content: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            attempt += 1
            print(f"Timeout occurred, retrying ({attempt}/{retries})")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
    else:
        print("Failed to retrieve content after many attempts.")
        return None
#using beautiful soup to parse HTML content
    soup = BeautifulSoup(html_content, "html.parser")
    
    topic_groups = soup.find_all("div", {"data-testid": "topic-group"})
    
    top_list = []
  
    for group in topic_groups:
        
        topics = group.find_all("li")
        for topic in topics:
            link = topic.find("a")
            if link:
                top_title = link.text.strip() 
                top_url = link["href"] 
                if not top_url.startswith("https"):
                    top_url = "https://www.healthline.com" + top_url 
                top_list.append({"topic": top_title, "url": top_url})
    
    return top_list

#purpose: saving new topics to file.
def save_topics(topics, filename="healthline_topics_mastersheet.json"):
    with open(filename, 'w') as file:
        json.dump(topics, file, indent=4)
    print(f"Data saved to {filename}")

#purpose: to get existing topics from json
def load_existing_topics(filename="healthline_topics_mastersheet.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        return None

#purpose: refresh to check if any new healthline topics have been added.
def refresh_topics():
    new_topics = get_topics()  
    if new_topics is None:
        return

    old_topics = load_existing_topics()  
    
    #purpose: to check if there are new topics and accordingly update json
    if old_topics != new_topics:
        save_topics(new_topics)
    else:
        print("The topics list is already updated.")

if __name__ == "__main__":
    refresh_topics()
