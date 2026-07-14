import customtkinter as ctk
from auth_manager import AuthManager
from launcher import RobloxLauncher
import threading
from tkinter import messagebox
import time
import logging
import os
import sys

# Directory detection for compiled environments
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

log_file_path = os.path.join(application_path, 'roblox_multi_debug.log')

logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(message)s',
    filemode='w',
    encoding='utf-8'
)

# Keep log files clean of verbose engine logs
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("WDM").setLevel(logging.WARNING)


class RobloxMultiApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Roblox-Multi Engine")
        self.geometry("620x540")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        logging.info("roblox-multi interface rendering...")
        
        try:
            self.auth = AuthManager()
            self.launcher = RobloxLauncher()
        except Exception as e:
            logging.critical(f"Kernel Initialization Exception: {e}", exc_info=True)
            messagebox.showerror("Kernel Panic", f"Failed to lock environment: {e}")
            return

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        self.check_auth_state()

    def check_auth_state(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        if self.auth.state == "LOCKED":
            self.show_password_screen()
        elif self.auth.state == "SETUP_REQUIRED":
            self.show_setup_screen()
        else:
            self.show_dashboard()

    def show_password_screen(self):
        ctk.CTkLabel(self.main_container, text="Roblox-Multi Vault Locked", font=("Arial", 22, "bold")).pack(pady=25)
        
        self.pass_entry = ctk.CTkEntry(self.main_container, placeholder_text="Security Key", show="*", width=240)
        self.pass_entry.pack(pady=10)
        
        ctk.CTkButton(self.main_container, text="Unlock Vault", width=140, command=self.unlock_vault).pack(pady=15)

    def unlock_vault(self):
        pwd = self.pass_entry.get()
        if self.auth.unlock(pwd):
            self.check_auth_state()
        else:
            messagebox.showerror("Access Denied", "Invalid Vault Token Key Parameters.")

    def show_setup_screen(self):
        ctk.CTkLabel(self.main_container, text="Initialize roblox-multi Vault", font=("Arial", 18, "bold")).pack(pady=25)
        
        self.new_pass = ctk.CTkEntry(self.main_container, placeholder_text="Create Vault Key (Optional)", show="*", width=260)
        self.new_pass.pack(pady=10)
        
        ctk.CTkButton(self.main_container, text="Build Vault", width=140, command=self.do_setup).pack(pady=15)

    def do_setup(self):
        pwd = self.new_pass.get()
        self.auth.setup_new(pwd if pwd else None)
        self.check_auth_state()

    def show_dashboard(self):
        ctk.CTkLabel(self.main_container, text="Roblox-Multi Control Board", font=("Arial", 22, "bold")).pack(pady=10)

        self.status_lbl = ctk.CTkLabel(self.main_container, text="Environment Status: Operational", text_color="#2ed573", font=("Arial", 13, "bold"))
        self.status_lbl.pack(pady=5)

        self.input_entry = ctk.CTkEntry(self.main_container, placeholder_text="Target ID / Username Parameter", width=300)
        self.input_entry.pack(pady=5)
        self.input_entry.insert(0, "116405044285330") 

        self.mode_var = ctk.StringVar(value="place")
        self.mode_switch = ctk.CTkSwitch(self.main_container, text="Target via Username Mode", variable=self.mode_var, onvalue="user", offvalue="place")
        self.mode_switch.pack(pady=5)

        btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.add_btn = ctk.CTkButton(btn_frame, text="Add New Session", width=140, command=self.add_account_thread)
        self.add_btn.grid(row=0, column=0, padx=5)

        self.launch_all_btn = ctk.CTkButton(btn_frame, text="Execute All", fg_color="#ff4757", hover_color="#ff6b81", width=140, command=self.launch_all)
        self.launch_all_btn.grid(row=0, column=1, padx=5)

        self.account_list = ctk.CTkScrollableFrame(self.main_container, height=220, label_text="Authenticated Native Profiles")
        self.account_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_list()

    def refresh_list(self):
        for widget in self.account_list.winfo_children():
            widget.destroy()

        if not self.auth.accounts:
            ctk.CTkLabel(self.account_list, text="No accounts inside secure vault metadata storage.", font=("Arial", 12, "italic")).pack(pady=20)
            return

        for username, data in self.auth.accounts.items():
            f = ctk.CTkFrame(self.account_list)
            f.pack(fill="x", pady=4, padx=5)
            
            ctk.CTkLabel(f, text=f"  {username}", font=("Arial", 13, "bold"), anchor="w").pack(side="left", padx=5, expand=True, fill="x")
            
            ctk.CTkButton(f, text="Fire Client", width=90, height=26,
                          command=lambda c=data['cookie']: self.launch_one(c)).pack(side="right", padx=5, pady=4)
            
            ctk.CTkButton(f, text="Unlink", width=50, height=26, fg_color="#57606f", hover_color="#2f3542",
                          command=lambda u=username: self.delete_account(u)).pack(side="right", padx=2, pady=4)

    def delete_account(self, username):
        if self.auth.delete_account(username):
            self.refresh_list()

    def add_account_thread(self):
        threading.Thread(target=self.add_account_logic, daemon=True).start()

    def add_account_logic(self):
        self.status_lbl.configure(text="Environment Status: Launching Isolated Authentication Container...", text_color="#eccc68")
        result = self.auth.add_account_via_browser()
        self.status_lbl.configure(text=f"Last Action Result: {result}", text_color="#ffffff")
        self.after(0, self.refresh_list)

    def launch_one(self, cookie):
        val = self.input_entry.get()
        mode = self.mode_var.get()
        logging.info(f"Triggering client lifecycle thread context. Mode: {mode}")
        threading.Thread(target=lambda: self.status_lbl.configure(text=f"Execution Message: {self.launcher.launch_account(cookie, val, mode)}")).start()

    def launch_all(self):
        val = self.input_entry.get()
        mode = self.mode_var.get()
        logging.info("Executing concurrent sequential launch mapping pipeline.")
        def _run():
            for name, data in self.auth.accounts.items():
                self.status_lbl.configure(text=f"Environment Status: Deploying {name}...")
                self.launcher.launch_account(data['cookie'], val, mode)
                time.sleep(6.5)
            self.status_lbl.configure(text="Environment Status: Deployment Complete", text_color="#2ed573")
        threading.Thread(target=_run).start()

if __name__ == "__main__":
    if sys.platform != "win32":
        print("roblox-multi Error: Windows OS context required.")
        sys.exit(1)
    try:
        app = RobloxMultiApp()
        app.mainloop()
    except Exception as e:
        logging.critical("roblox-multi Main Runtime Thread Crash Exception Handled.", exc_info=True)