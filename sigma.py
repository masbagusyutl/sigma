import json
import time
import datetime
from colorama import Fore, Style, init
import requests
from fake_useragent import UserAgent

init(autoreset=True)

def print_welcome_message():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
          """)
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop Sigma")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop")

def load_accounts(file_path='data.txt'):
    try:
        with open(file_path, 'r') as file:
            accounts = [line.strip() for line in file if line.strip()]
        return accounts
    except FileNotFoundError:
        print(Fore.RED + "File data.txt tidak ditemukan. Pastikan file ada di direktori yang sama dengan program ini.")
        return []

def display_user_info(user_info, wallet, balance):
    print(Fore.CYAN + "Informasi Pengguna:")
    print(Fore.CYAN + f" - Username: {user_info.get('username')}")
    print(Fore.CYAN + f" - Premium: {'Ya' if user_info.get('is_premium') else 'Tidak'}")
    print(Fore.CYAN + f" - Balance: {balance} SIGMA")

def claim_task_done(task_name, task_id, auth_token, session):
    try:
        url = "https://apisigma.no.pics/api/v1/task/claim/done"
        payload = {"id": task_id}
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
        response = session.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(Fore.GREEN + f"Tugas '{task_name}' berhasil masuk tahap selesai awal.")
            return True
        else:
            print(Fore.RED + f"Gagal menyelesaikan tahap awal tugas '{task_name}'. Status kode: {response.status_code}")
            return False
    except Exception as e:
        print(Fore.RED + f"Error saat menyelesaikan tahap awal tugas '{task_name}': {str(e)}")
        return False

def claim_task_finish(task_name, task_id, auth_token, session):
    try:
        url = "https://apisigma.no.pics/api/v1/task/claim/finish"
        payload = {"id": task_id}
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }
        response = session.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(Fore.GREEN + f"Tugas '{task_name}' berhasil diproses hingga selesai.")
            return True
        else:
            print(Fore.RED + f"Gagal menyelesaikan tahap akhir tugas '{task_name}'. Status kode: {response.status_code}")
            return False
    except Exception as e:
        print(Fore.RED + f"Error saat menyelesaikan tahap akhir tugas '{task_name}': {str(e)}")
        return False

def get_all_tasks(auth_token, session):
    try:
        url = "https://apisigma.no.pics/api/v1/task/getAllTasks"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json",
        }
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(Fore.GREEN + "Daftar tugas yang berhasil diambil:")
            for task in tasks:
                status = task["status"]
                if status == "TASK_COMPLETE_FINISHED":
                    print(Fore.YELLOW + f" - {task['name']}: (Sudah selesai)")
                else:
                    print(Fore.GREEN + f" - {task['name']}: (Akan Diproses)")

            # Proses klaim tugas yang belum selesai
            for task in tasks:
                if task["status"] == "TASK_NOT_COMPLETED":
                    print(Fore.YELLOW + f"Memproses tugas: {task['name']}")
                    if claim_task_done(task["name"], task["id"], auth_token, session):
                        claim_task_finish(task["name"], task["id"], auth_token, session)
            return tasks
        else:
            print(Fore.RED + f"Gagal mengambil tugas dengan status kode: {response.status_code}")
            return []
    except Exception as e:
        print(Fore.RED + f"Error saat mengambil tugas: {str(e)}")
        return []

def process_account(account, user_agent, session):
    print(Fore.YELLOW + f"Mencoba masuk akun...")
    try:
        # Request auth
        url = "https://apisigma.no.pics/api/v1/user/auth?method=telegram"
        payload = {"init_data": account}
        headers = {
            "User-Agent": user_agent,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = session.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get("user", {})
            wallet = data.get("wallet")
            balance = data.get("balance", 0)
            display_user_info(user_info, wallet, balance)

            # Mendapatkan semua tugas setelah autentikasi
            auth_token = data.get("token")
            if auth_token:
                get_all_tasks(auth_token, session)
            else:
                print(Fore.RED + "Token autentikasi tidak ditemukan.")
        else:
            print(Fore.RED + f"Gagal memproses akun dengan status kode: {response.status_code}")
            print(Fore.YELLOW + "Tips: Periksa koneksi internet atau format data di file data.txt")
    except Exception as e:
        print(Fore.RED + f"Error saat memproses akun: {str(e)}")
        print(Fore.YELLOW + "Tips: Coba ulangi proses ini atau periksa format file data.txt.")

def countdown_one_day():
    print(Fore.BLUE + "Memulai hitung mundur 1 hari...")
    target_time = datetime.datetime.now() + datetime.timedelta(days=1)
    while datetime.datetime.now() < target_time:
        remaining = target_time - datetime.datetime.now()
        print(Fore.BLUE + f"Hitung mundur: {str(remaining).split('.')[0]}", end="\r")
        time.sleep(1)
    print(Fore.GREEN + "\nWaktu 1 hari selesai. Memulai ulang proses.")

def main():
    print_welcome_message()
    accounts = load_accounts()
    
    if not accounts:
        print(Fore.RED + "Tidak ada akun yang ditemukan di file data.txt.")
        return
    
    print(Fore.CYAN + f"Jumlah akun yang ditemukan: {len(accounts)}")
    session = requests.Session()
    ua = UserAgent()
    
    for idx, account in enumerate(accounts, start=1):
        print(Fore.CYAN + f"Mengolah akun {idx}/{len(accounts)}")
        user_agent = ua.random  # Generate a random User-Agent
        process_account(account, user_agent, session)
        time.sleep(5)  # Jeda 5 detik antar akun
    
    print(Fore.GREEN + "Semua akun telah diproses.")
    countdown_one_day()
    main()  # Mulai ulang proses

if __name__ == "__main__":
    main()
