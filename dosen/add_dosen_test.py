from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import random
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from login.login_page import LoginPage

import os
from dotenv import load_dotenv

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))


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

    # ========== 2️⃣ NAVIGASI KE HALAMAN MAHASISWA ==========
    try:
        driver.get(f"{APP_URL}/dosen")
        dashboard_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Daftar Dosen" in dashboard_text
        print("✅ Functional Test 2: Halaman Dosen terbuka")
    except Exception as e:
        print("❌ Functional Test 2 gagal (Akses halaman dosen):", e)

    # ========== 3️⃣ BUKA MODAL TAMBAH ==========
    try:
        tambah_button = driver.find_element(By.XPATH, "//button[contains(., 'Tambah')]")
        tambah_button.click()

        modal = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal")))
        assert "Tambah" in modal.text.lower()
        print("✅ Functional Test 3: Modal Tambah dosen terbuka")
    except Exception as e:
        print("❌ Functional Test 3 gagal (Modal tambah):", e)

    # ========== 4️⃣ ISI FORM ==========
    try:
        rand_num = random.randint(1000, 9999)

        driver.find_element(By.ID, "username").send_keys(f"mhs_{rand_num}")
        driver.find_element(By.ID, "nidn").send_keys(str(23000000 + rand_num))
        driver.find_element(By.ID, "nama").send_keys(faker.name())
        driver.find_element(By.ID, "email").send_keys(faker.email())
        driver.find_element(By.ID, "no_tlp").send_keys(faker.phone_number())
        driver.find_element(By.ID, "alamat").send_keys(faker.address())

        driver.find_element(By.ID, "password").send_keys("password123")

        # Upload foto
        driver.find_element(By.ID, "foto_profile").send_keys(
            os.path.join(base_dir, 'images', 'ram.jpg')
        )

        print("✅ Functional Test 4: Semua field berhasil diisi")
    except Exception as e:
        print("❌ Functional Test 4 gagal (Isi form):", e)

    # ========== 5️⃣ SUBMIT FORM ==========
    try:
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        print("⏳ Menunggu notifikasi...")

        notif = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "swal2-popup")))
        notif_text = notif.text

        if "berhasil" in notif_text.lower():
            print("✅ Functional Test 5: Data Mahasiswa berhasil ditambahkan")
        else:
            print("❌ Functional Test 5: Gagal menambahkan mahasiswa — Pesan:", notif_text)
    except Exception as e:
        print("❌ Functional Test 5 gagal (Submit):", e)

except Exception as e:
    print("🔥 Terjadi error utama:", e)

finally:
    driver.quit()
    print("🔚 Test selesai - browser ditutup.")
