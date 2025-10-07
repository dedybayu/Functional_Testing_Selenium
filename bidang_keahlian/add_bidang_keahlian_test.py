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
        login_page.login(USERNAME, PASSWORD)
        
        dashboard_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Dashboard Admin" in dashboard_text
        print("✅ Functional Test 1: Login berhasil")
    except Exception as e:
        print("❌ Functional Test 1 gagal (Login):", e)

    # ========== 2️⃣ NAVIGASI KE HALAMAN MAHASISWA ==========
    try:
        driver.get(f"{APP_URL}/bidangKeahlian")
        dashboard_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Daftar Bidang Keahlian" in dashboard_text
        print("✅ Functional Test 2: Halaman Bidang Keahlian terbuka")
    except Exception as e:
        print("❌ Functional Test 2 gagal (Akses halaman Bidang Keahlian):", e)

    # ========== 3️⃣ BUKA MODAL TAMBAH ==========
    try:
        # Klik tombol tambah
        tambah_button = driver.find_element(By.XPATH, "//button[contains(normalize-space(.), 'Tambah')]")
        tambah_button.click()

        # Tunggu modal muncul
        modal = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "modal")))

        # Tunggu sampai teks muncul di modal title
        wait.until(
            EC.text_to_be_present_in_element((By.CLASS_NAME, "modal-title"), "Tambah Data Bidang Keahlian")
        )

        modal_title = driver.find_element(By.CLASS_NAME, "modal-title").text
        assert "Tambah Data Bidang Keahlian" in modal_title
        print("✅ Modal 'Tambah Data Bidang Keahlian' berhasil terbuka.")
    except Exception as e:
        print("❌ Functional Test 3 gagal (Modal tambah):", e)

    # ========== 4️⃣ ISI FORM ==========
    try:
        rand_num = random.randint(1000, 9999)

        driver.find_element(By.ID, "bidang_keahlian_kode").send_keys(f"BID_{rand_num}")
        driver.find_element(By.ID, "bidang_keahlian_nama").send_keys(faker.word().capitalize())

        # Tunggu agar form-nya siap (optional)
        time.sleep(1)

        # Temukan elemen <select> asli
        dropdown = driver.find_element(By.ID, "kategori_bidang_keahlian_id")

        # Bungkus dengan Select helper Selenium
        select = Select(dropdown)

        # Ambil semua opsi kecuali yang disabled / placeholder
        options = [opt for opt in select.options if opt.get_attribute("disabled") is None]

        print("Jumlah opsi:", len(options))
        for opt in options:
            print("-", opt.text.strip())

        # Pilih acak
        if len(options) > 0:
            selected_option = random.choice(options)
            print("✅ Memilih:", selected_option.text.strip())
            select.select_by_visible_text(selected_option.text.strip())
        else:
            print("❌ Tidak ada opsi yang bisa dipilih.")

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
            print("✅ Functional Test 5: Data Bidang Keahlian berhasil ditambahkan")
        else:
            print("❌ Functional Test 5: Gagal menambahkan bidang keahlian — Pesan:", notif_text)
    except Exception as e:
        print("❌ Functional Test 5 gagal (Submit):", e)

except Exception as e:
    print("🔥 Terjadi error utama:", e)

finally:
    driver.quit()
    print("🔚 Test selesai - browser ditutup.")
