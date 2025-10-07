from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import random
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from login.login_page import LoginPage

import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))


# Setup driver (Chrome)
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)
faker = Faker("id_ID")

# Muat file .env
load_dotenv()

# Ambil username dan password dari env
USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")
APP_URL = os.getenv("APP_URL")

try:
    # ========== 1️⃣ LOGIN TEST ==========
    try:
        login_page = LoginPage(driver, APP_URL)
        login_page.open()
        login_page.login("admin", "admin123")

        dashboard_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Dashboard Admin" in dashboard_text
        print("✅ Functional Test 1: Login berhasil")
    except Exception as e:
        print("❌ Functional Test 1 gagal (Login):", e)

    # ========== 2️⃣ NAVIGASI KE HALAMAN Rekomendasi ==========
    try:
        driver.get(f"{APP_URL}/rekomendasi")
        dashboard_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Daftar Rekomendasi" in dashboard_text
        print("✅ Functional Test 2: Halaman Rekomendasi terbuka")
    except Exception as e:
        print("❌ Functional Test 2 gagal (Akses halaman Rekomendasi):", e)

    # ========== 3️⃣ BUKA MODAL TAMBAH ==========
    try:
        tambah_button = driver.find_element(By.XPATH, "//button[contains(., 'Perbarui Data')]")
        tambah_button.click()

        modal = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal")))
        assert "Perbarui Data Rekomendasi" in modal.text
        print("✅ Functional Test 3: Modal Tambah Rekomendasi terbuka")
    except Exception as e:
        print("❌ Functional Test 3 gagal (Modal tambah):", e)

except Exception as e:
    print("🔥 Terjadi error utama:", e)

finally:
    driver.quit()
    print("🔚 Test selesai - browser ditutup.")
