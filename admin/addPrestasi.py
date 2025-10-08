import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

URL = "https://presma.dbsnetwork.my.id/prestasi"
TIMEOUT = 20

def random_name(prefix="Auto Prestasi"):
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix} {suffix}"

def random_date_last_month_to_today():
    today = datetime.today().date()
    start = today - timedelta(days=30)
    random_day = start + timedelta(days=random.randint(0, (today - start).days))
    return random_day.strftime("%Y-%m-%d")

def pick_select2_option(driver, wait, container_id: str, result_id: str = None, min_index: int = 1, max_index: int = 1):
    # Klik container utama Select2
    container = wait.until(EC.element_to_be_clickable((By.ID, container_id)))
    container.click()

    # Jika disediakan result_id, pilih langsung berdasarkan ID option
    if result_id:
        option = wait.until(EC.element_to_be_clickable((By.ID, result_id)))
        driver.execute_script("arguments[0].scrollIntoView(true);", option)
        option.click()
        return

    # Fallback: pilih secara acak dalam rentang indeks
    options = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'ul.select2-results__options li.select2-results__option[aria-disabled="false"]')
    ))
    if not options:
        raise RuntimeError(f"No options found for {container_id}")

    target = random.randint(min_index, min(max_index, len(options))) - 1
    driver.execute_script("arguments[0].scrollIntoView(true);", options[target])
    options[target].click()

def upload_file(wait, field_id: str, file_path: Path):
    elem = wait.until(EC.presence_of_element_located((By.ID, field_id)))
    elem.send_keys(str(file_path))

def get_result_message(driver, wait):
    try:
        alert = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert")))
        txt = alert.text.strip()
        status = "success" if "success" in txt.lower() or "berhasil" in txt.lower() else "failed"
        return status, txt
    except Exception:
        pass

    try:
        title = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".swal2-container .swal2-title")))
        body = driver.find_element(By.CSS_SELECTOR, ".swal2-container .swal2-html-container").text if driver.find_elements(By.CSS_SELECTOR, ".swal2-container .swal2-html-container") else ""
        txt = f"{title.text.strip()} {body}".strip()
        status = "success" if "success" in txt.lower() or "berhasil" in txt.lower() else "failed"
        return status, txt
    except Exception:
        pass

    toasts = driver.find_elements(By.CSS_SELECTOR, ".toast .toast-body, .toast")
    if toasts:
        txt = " ".join(t.text.strip() for t in toasts).strip()
        status = "success" if "success" in txt.lower() or "berhasil" in txt.lower() else "failed"
        return status, txt

    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "berhasil" in body_text or "success" in body_text:
        return "success", "Operation reported success."
    if "gagal" in body_text or "error" in body_text or "failed" in body_text:
        return "failed", "Operation reported failure."
    return "unknown", "No explicit result message found."

def resolve_brave_path():
    env_path = os.environ.get("BRAVE_BINARY")
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    candidates += [
        Path(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
        Path(r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"),
        Path(r"C:\Users\GIO\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for p in candidates:
        if p and p.exists():
            return str(p)
    return None

def main():
    base_dir = Path(__file__).resolve().parents[1]
    files = {
        "file_sertifikat": base_dir / "1.png",
        "file_bukti_foto": base_dir / "2.png",
        "file_surat_tugas": base_dir / "3.png",
        "file_surat_undangan": base_dir / "4.png",
        "file_proposal": base_dir / "5.pdf",
    }

    chrome_options = Options()

    # ==== 🔧 GUNAKAN PROFIL PRIBADI BRAVE ====
    brave_binary = resolve_brave_path()
    if not brave_binary:
        raise FileNotFoundError("Brave browser not found. Install Brave or set BRAVE_BINARY env var to brave.exe")

    chrome_options.binary_location = brave_binary
    user_data_dir = r"C:\Users\GIO\AppData\Local\BraveSoftware\Brave-Browser\User Data"
    profile_dir = "Default"  # ganti ke 'Profile 1' kalau kamu pakai profil kedua

    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument(f"--profile-directory={profile_dir}")

    # Opsional: sembunyikan teks “controlled by automated software”
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Tambahan kenyamanan
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, TIMEOUT)

    try:
        driver.get(URL)

        add_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            '//button[contains(@onclick,"/prestasi/create") and contains(@class,"btn-success")]'
        )))
        add_btn.click()

        nama = wait.until(EC.visibility_of_element_located((By.ID, "prestasi_nama")))
        nama.clear()
        nama.send_keys(random_name())

        # Gunakan ID fixed untuk masing-masing Select2
        pick_select2_option(driver, wait, "select2-prestasi_mahasiswa-container", result_id="select2-prestasi_mahasiswa-result-7qq6-2")
        pick_select2_option(driver, wait, "select2-prestasi_lomba-container", result_id="select2-prestasi_lomba-result-cu9n-3")
        pick_select2_option(driver, wait, "select2-prestasi_dosbim-container", result_id="select2-prestasi_dosbim-result-xmy3-2")

        # # Manual selection untuk prestasi_mahasiswa (pilih value pertama secara statis)
        # mahasiswa_container = wait.until(EC.element_to_be_clickable((By.ID, "select2-prestasi_mahasiswa-container")))
        # mahasiswa_container.click()
        
        # # Tunggu dropdown terbuka dan pilih option pertama
        # first_option = wait.until(EC.element_to_be_clickable((
        #     By.CSS_SELECTOR, 
        #     'ul.select2-results__options li.select2-results__option[aria-disabled="false"]:first-child'
        # )))
        # first_option.click()

        tanggal = wait.until(EC.element_to_be_clickable((By.ID, "tanggal_perolehan")))
        tanggal.clear()
        tanggal.send_keys(random_date_last_month_to_today())

        # Tetap acak untuk juara (tidak ada ID fixed yang diberikan)
        pick_select2_option(driver, wait, "select2-prestasi_juara-container", min_index=1, max_index=3)

        for field_id, path in files.items():
            if not path.exists():
                alt = Path(__file__).resolve().parent / path.name
                path = alt if alt.exists() else path
                
            upload_file(wait, field_id, path)

        submit = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, ".modal.show .btn.btn-primary, .btn.btn-primary"
        )))
        submit.click()

        status, message = get_result_message(driver, WebDriverWait(driver, TIMEOUT))
        print(f"Result: {status.upper()} - {message}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
