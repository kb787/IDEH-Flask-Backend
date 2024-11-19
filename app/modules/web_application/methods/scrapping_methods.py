import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import validators
import whois


class WebScraperMethods:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

    def validate_url(self, url):
        return validators.url(url)

    def extract_email(self, text):
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.findall(email_pattern, text)

    def scrape_url(self, url):
        try:
            if not self.validate_url(url):
                raise ValueError("Invalid URL")
            domain_info = whois.whois(url)
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            title = soup.title.string if soup.title else ""
            description_tag = soup.find("meta", attrs={"name": "description"})
            description = description_tag["content"] if description_tag else ""
            text_content = soup.get_text()
            emails = self.extract_email(text_content)
            source_type = self.determine_source_type(url)
            scraped_data = {
                "url": url,
                "name": self.extract_name(soup),
                "about": self.extract_about(soup),
                "source_type": source_type,
                "industry": self.extract_industry(text_content),
                "page_content_type": self.determine_page_type(soup),
                "contact": self.extract_contact(soup),
                "email": emails[0] if emails else None,
                "title": title,
                "description": description,
                "raw_content": text_content,
            }

            return scraped_data

        except Exception as e:
            raise Exception(f"Scraping error: {str(e)}")

    def determine_source_type(self, url):
        domain_mapping = {
            "linkedin.com": "Social Media - Professional",
            "twitter.com": "Social Media - Personal",
            "facebook.com": "Social Media - Personal",
            "github.com": "Developer Profile",
            "medium.com": "Blog/Publishing Platform",
        }

        for domain, type_name in domain_mapping.items():
            if domain in url:
                return type_name
        return "Website"

    def extract_name(self, soup):
        name_candidates = soup.find_all(["h1", "title", "meta"])
        for candidate in name_candidates:
            if candidate.get("property") == "og:title":
                return candidate.get("content")
        return ""

    def extract_about(self, soup):
        about_sections = soup.find_all(
            ["div", "p"], class_=re.compile(r"about|description|bio", re.IGNORECASE)
        )
        return " ".join([section.get_text() for section in about_sections])[:500]

    def extract_industry(self, text):
        industries = [
            "Technology",
            "Finance",
            "Healthcare",
            "Education",
            "Marketing",
            "Engineering",
        ]
        for industry in industries:
            if industry.lower() in text.lower():
                return industry
        return "Unknown"

    def extract_contact(self, soup):
        contact_tags = soup.find_all(
            ["a"], href=re.compile(r"tel:|contact", re.IGNORECASE)
        )
        return contact_tags[0].get("href") if contact_tags else ""

    def determine_page_type(self, soup):
        if soup.find("article"):
            return "Blog/Article"
        elif soup.find("profile"):
            return "Profile Page"
        elif soup.find("form"):
            return "Contact/Landing Page"
        return "General Website"

    def close(self):
        self.driver.quit()
