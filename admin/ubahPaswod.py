from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os, sys

# ====== KONFIGURASI ======
URL_TARGET = "https://presma.dbsnetwork.my.id/profile/admin"
OLD_PASSWORD = "admin123"
NEW_PASSWORD = "admin456" #pw skrg

# Jika ingin memakai profil Chrome pribadi, isi USER_DATA_DIR dan PROFILE_DIR.
USE_PROFILE = False
USER_DATA_DIR = r"C:\Users\GIO\AppData\Local\Google\Chrome\User Data"
PROFILE_DIR = "Default"

CHROME_DRIVER_PATH = None  # None jika chromedriver ada di PATH

# Kredensial login yang diminta user
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"

# Timeout
WAIT_FOR_TARGET_TIMEOUT = 20
SHORT_WAIT = 5

# ====== SETUP CHROME OPTIONS ======
options = webdriver.ChromeOptions()
options.add_argument("--disable-notifications")
options.add_argument("--start-maximized")
if USE_PROFILE:
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.add_argument(f"--profile-directory={PROFILE_DIR}")

service = Service(CHROME_DRIVER_PATH) if CHROME_DRIVER_PATH else None
driver = webdriver.Chrome(service=service, options=options) if service else webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

def save_debug(name_prefix="debug"):
    ts = int(time.time())
    screenshot = f"{name_prefix}_{ts}.png"
    try:
        driver.save_screenshot(screenshot)
        print(f"[DEBUG] Screenshot saved: {screenshot}")
    except Exception as e:
        print("[DEBUG] Gagal menyimpan screenshot:", e)
    try:
        dom = driver.execute_script("return document.documentElement.outerHTML;")
        dom_file = f"{name_prefix}_{ts}.html"
        with open(dom_file, "w", encoding="utf-8") as f:
            f.write(dom[:20000])
        print(f"[DEBUG] Snapshot DOM saved: {dom_file} (truncated)")
    except Exception as e:
        print("[DEBUG] Gagal menyimpan DOM snapshot:", e)

def attempt_login_if_needed():
    """
    Jika diarahkan ke halaman login (ada id='username' dan id='password'),
    isi kredensial dan submit.
    """
    try:
        # cek keberadaan field login (id='username' dan id='password')
        username_el = None
        password_el = None
        try:
            username_el = driver.find_element(By.ID, "username")
            password_el = driver.find_element(By.ID, "password")
        except Exception:
            # jika tidak ada langsung return False
            return False

        if username_el and password_el:
            print("[INFO] Form login terdeteksi. Melakukan login otomatis...")
            username_el.clear()
            username_el.send_keys(LOGIN_USERNAME)
            password_el.clear()
            password_el.send_keys(LOGIN_PASSWORD)

            # coba klik tombol submit bila ada
            submitted = False
            # cari tombol submit di sekitar form
            try:
                # tombol dengan type='submit'
                btn_submit = driver.find_element(By.XPATH, "//button[@type='submit' or contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'LOGIN')]")
                if btn_submit.is_displayed() and btn_submit.is_enabled():
                    btn_submit.click()
                    submitted = True
                    print("[INFO] Menekan tombol submit untuk login.")
            except Exception:
                pass

            if not submitted:
                # fallback: tekan ENTER pada field password
                password_el.send_keys(Keys.ENTER)
                print("[INFO] Menekan ENTER pada field password sebagai fallback submit.")

            # tunggu sedikit agar proses login berlangsung
            try:
                WebDriverWait(driver, WAIT_FOR_TARGET_TIMEOUT).until(
                    lambda d: "/profile/admin" in d.current_url.lower()
                )
                print("[INFO] Redirect ke /profile/admin setelah login.")
                return True
            except Exception:
                print("[WARN] Setelah submit login, belum redirect ke /profile/admin dalam timeout.")
                return False

    except Exception as ex:
        print("[ERROR] Gagal saat mencoba login otomatis:", ex)
        return False

# ====== RUN SCRIPT ======
try:
    # buka target (bisa redirect ke login jika belum ada session)
    driver.get(URL_TARGET)
    print(f"[INFO] Membuka: {URL_TARGET}")

    # tunggu sampai readyState complete
    try:
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    except Exception:
        print("[WARN] readyState tidak complete setelah timeout.")

    # Jika URL belum mengandung /profile/admin, coba cek login dan lakukan login jika form ada
    if "/profile/admin" not in driver.current_url.lower():
        print("[INFO] Belum di /profile/admin. current_url =", driver.current_url)
        logged = attempt_login_if_needed()
        if not logged:
            # Jika login tidak dilakukan (tidak ada form) atau gagal, simpan debug & hentikan
            print("[ERROR] Tidak berhasil login otomatis atau tidak menemukan form login.")
            save_debug("login_needed")
            raise RuntimeError("Perlu login manual atau gunakan profil Chrome yang sudah login.")
    else:
        print("[INFO] Sudah berada di /profile/admin (session aktif).")

    # Pastikan sekarang sudah di halaman /profile/admin
    try:
        WebDriverWait(driver, WAIT_FOR_TARGET_TIMEOUT).until(
            lambda d: "/profile/admin" in d.current_url.lower()
        )
        print("[INFO] Konfirmasi: berada di URL", driver.current_url)
    except Exception:
        print("[ERROR] Gagal memastikan URL /profile/admin setelah login.")
        save_debug("post_login_not_on_profile")
        raise RuntimeError("Tidak berada di halaman /profile/admin setelah login.")

    # --- Lanjut workflow: klik edit, isi password lama & baru, klik Simpan ---
    # 1) Klik tombol edit (class btn-warning)
    edit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-warning")))
    edit_button.click()
    print("[STEP] Klik tombol Edit -> BERHASIL")

    # 2) Isi password lama
    old_pass = wait.until(EC.presence_of_element_located((By.NAME, "old_password")))
    old_pass.clear()
    old_pass.send_keys(OLD_PASSWORD)
    print("[STEP] Isi password lama -> BERHASIL")

    # 3) Isi password baru
    new_pass = wait.until(EC.presence_of_element_located((By.NAME, "new_password")))
    new_pass.clear()
    new_pass.send_keys(NEW_PASSWORD)
    print("[STEP] Isi password baru -> BERHASIL")

    # 4) Klik Simpan
    simpan_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(@class, 'btn-primary') and normalize-space(text())='Simpan']")
        )
    )
    simpan_button.click()
    print("[ACTION] Tombol 'Simpan' diklik — menunggu popup...")

    # 5) Tunggu popup dan baca pesan
    try:
        swal_popup = WebDriverWait(driver, SHORT_WAIT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-popup")))
        try:
            message_el = swal_popup.find_element(By.CSS_SELECTOR, ".swal2-html-container")
            message_text = message_el.text.strip()
        except Exception:
            message_text = swal_popup.text.strip()

        print("[RESULT] Popup ditemukan. Pesan:", message_text)
        status = "TIDAK JELAS"
        low = message_text.lower()
        if any(k in low for k in ["berhasil", "sukses", "success"]):
            status = "BERHASIL"
        elif any(k in low for k in ["gagal", "failed", "error"]):
            status = "GAGAL"
        print(f"[STATUS] Hasil deteksi: {status} (berdasarkan teks popup)")

    except Exception as e:
        print("[WARN] Popup Swal2 tidak muncul setelah klik Simpan:", e)
        save_debug("no_popup_after_simpan")
        status = "TIDAK JELAS"

    # 6) Klik OK pada popup (jika ada)
    try:
        ok_button = WebDriverWait(driver, SHORT_WAIT).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class,'swal2-confirm') and normalize-space(text())='OK']")
            )
        )
        ok_button.click()
        print("[STEP] Klik tombol 'OK' pada popup -> BERHASIL")
    except Exception as e:
        print("[WARN] Tombol OK tidak ditemukan atau gagal diklik:", e)

    # Final message
    if status == "BERHASIL":
        print("🎉 Penggantian password tampak BERHASIL.")
    elif status == "GAGAL":
        print("❌ Penggantian password tampak GAGAL — cek pesan & network log.")
    else:
        print("⚠️ Status tidak jelas — periksa screenshot/DOM yang tersimpan.")

    time.sleep(2)

except Exception as e:
    print("!! SCRIPT ERROR:", e)
    try:
        save_debug("exception")
    except Exception:
        pass
finally:
    try:
        driver.quit()
    except Exception:
        pass
    print("[INFO] Selesai — browser ditutup.")
