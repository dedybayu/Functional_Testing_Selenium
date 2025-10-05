from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Setup driver (Chrome)
driver = webdriver.Chrome()

try:
    # 1. Buka halaman login
    driver.get("https://presma.dbsnetwork.my.id/login")

    # 2. Masukkan username
    username = driver.find_element(By.ID, "username")
    username.send_keys("admin")

    # 3. Masukkan password
    password = driver.find_element(By.ID, "password")
    password.send_keys("admin123")

    # 4. Klik tombol login
    login_button = driver.find_element(By.ID, "btn-login")
    login_button.click()
    
    # 5. Verifikasi hasil (cek teks pada halaman, bukan title)
    dashboard_text = driver.find_element(By.TAG_NAME, "body").text

    assert "Dashboard Admin" in dashboard_text
    print("✅ Functional Test: Login berhasil (teks ditemukan di halaman)")

except Exception as e:
    print("❌ Functional Test gagal:", e)

finally:
    driver.quit()
