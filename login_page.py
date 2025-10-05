from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
from urllib.parse import urljoin
# Muat file .env
load_dotenv()

APP_URL = os.getenv("APP_URL")

class LoginPage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.url = urljoin(base_url, "login") 

        # Locator
        self.username_input = (By.ID, "username")
        self.password_input = (By.ID, "password")
        self.login_button = (By.ID, "btn-login")

    def open(self):
        """Buka halaman login"""
        self.driver.get(self.url)

    def login(self, username, password):
        """Isi form login lalu klik tombol"""
        self.driver.find_element(*self.username_input).send_keys(username)
        self.driver.find_element(*self.password_input).send_keys(password)
        self.driver.find_element(*self.login_button).click()
