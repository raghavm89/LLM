import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def user_prompt_for(website):
    user_prompt = f"You are looking at a website titled {website.title}"
    user_prompt += "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too.\n\n"
    user_prompt += website.text
    return user_prompt

def messages_for(system_prompt,website):
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_for(website)}
        ]

def summarize(system_prompt,url):
    website = Website(url)

    response = openai.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages_for(system_prompt,website)
    )
    return response.choices[0].message.content
    

def display_summary(system_prompt,url):
    summary = summarize(system_prompt,url)
    display(Markdown(summary).data)





# Check the key
def check_key(api_key):
    if not api_key:
        print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
    elif not api_key.startswith("sk-proj-"):
        print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
    elif api_key.strip() != api_key:
        print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
    else:
        print("API key found and looks good so far!")


class Website:

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    def __init__(self, url):
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        
        #response = requests.get(url, headers=self.headers)
        #soup = BeautifulSoup(response.content, 'html.parser')
       
        firefox_options = Options()
        firefox_options.headless = True
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--disable-gpu')
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Firefox(options=firefox_options)
        driver.get(url)
        html = driver.page_source
        driver.quit()
        soup = BeautifulSoup(html,'html.parser')

        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)



if __name__ == "__main__":
    load_dotenv(override=True)
    api_key = os.getenv('OPENAI_API_KEY')
    check_key(api_key)
    openai = OpenAI()

    system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

    
    #display_summary(system_prompt,"https://edwarddonner.com")
    display_summary(system_prompt,"https://amazon.com")

    