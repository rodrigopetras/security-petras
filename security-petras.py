#!/usr/bin/env python3
# Security Petras V6 - Ultimate Security Toolkit Installer

import os
import subprocess
import sys
import platform
import threading
from tkinter import *
from tkinter import ttk, messagebox

APP_NAME = "Security Petras V6"
INSTALL_DIR = os.path.expanduser("~/.security-petras")

# ==============================
# DETECT DISTRO
# ==============================
def detect_distro():
    if os.path.exists("/etc/debian_version"):
        return "debian"
    elif os.path.exists("/etc/arch-release"):
        return "arch"
    elif os.path.exists("/etc/redhat-release"):
        return "redhat"
    return "unknown"

DISTRO = detect_distro()

# ==============================
# TOOL DATABASE
# ==============================
TOOLS = {
    "Information Gathering": {
        "nmap": "Network scanner",
        "theharvester": "OSINT email/domain gathering",
        "dnsenum": "DNS enumeration"
    },
    "Vulnerability Analysis": {
        "nikto": "Web vulnerability scanner",
        "sqlmap": "SQL injection testing",
        "lynis": "Security auditing tool"
    },
    "Exploitation": {
        "metasploit": "Exploit framework",
        "searchsploit": "Exploit database search"
    },
    "Wireless": {
        "aircrack-ng": "WiFi cracking suite",
        "reaver": "WPS attack tool"
    },
    "Web": {
        "burpsuite": "Web pentest proxy",
        "wpscan": "WordPress scanner"
    },
    "Passwords": {
        "hydra": "Password brute force",
        "john": "Password cracker"
    },
    "Forensics": {
        "volatility": "Memory forensics",
        "binwalk": "Firmware analysis"
    }
}

# ==============================
# INSTALL COMMANDS
# ==============================
def get_install_cmd(tool):
    if DISTRO == "debian":
        return ["sudo", "apt", "install", "-y", tool]
    elif DISTRO == "arch":
        return ["sudo", "pacman", "-S", "--noconfirm", tool]
    elif DISTRO == "redhat":
        return ["sudo", "dnf", "install", "-y", tool]
    return None

# ==============================
# INSTALL TOOL
# ==============================
def install_tool(tool, log_box, progress, stealth=False):
    cmd = get_install_cmd(tool)

    if not cmd:
        log_box.insert(END, f"❌ Unsupported distro for {tool}\n")
        return

    try:
        if stealth:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            for line in process.stdout:
                log_box.insert(END, line)
                log_box.see(END)

        progress.step(5)

    except Exception as e:
        log_box.insert(END, f"❌ Error installing {tool}: {e}\n")

# ==============================
# INSTALL THREAD
# ==============================
def install_selected(selected_tools, log_box, progress, stealth):
    for tool in selected_tools:
        log_box.insert(END, f"\n🔧 Installing {tool}...\n")
        install_tool(tool, log_box, progress, stealth)

    log_box.insert(END, "\n✅ Installation complete!\n")

# ==============================
# GUI
# ==============================
class App:

    def __init__(self, root):
        self.root = root
        root.title(APP_NAME)
        root.geometry("1000x600")
        root.configure(bg="#0a0a0a")

        self.selected_tools = []
        self.check_vars = {}

        # Sidebar
        self.sidebar = Frame(root, bg="#111111", width=250)
        self.sidebar.pack(side=LEFT, fill=Y)

        Label(self.sidebar, text="Security Petras", fg="#00ff00", bg="#111111", font=("Arial", 14, "bold")).pack(pady=10)

        for category in TOOLS:
            btn = Button(self.sidebar, text=category, bg="#111", fg="#0f0",
                         command=lambda c=category: self.load_category(c))
            btn.pack(fill=X, padx=10, pady=2)

        # Main area
        self.main = Frame(root, bg="#0a0a0a")
        self.main.pack(side=RIGHT, expand=True, fill=BOTH)

        self.tools_frame = Frame(self.main, bg="#0a0a0a")
        self.tools_frame.pack(fill=BOTH, expand=True)

        # Bottom
        bottom = Frame(root, bg="#111")
        bottom.pack(side=BOTTOM, fill=X)

        self.progress = ttk.Progressbar(bottom, length=400)
        self.progress.pack(pady=5)

        self.log = Text(bottom, height=8, bg="black", fg="green")
        self.log.pack(fill=X)

        # Buttons
        btn_frame = Frame(bottom, bg="#111")
        btn_frame.pack()

        Button(btn_frame, text="Install Selected", command=self.start_install).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Install Full", command=self.install_full).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Update Tool", command=self.update_tool).pack(side=LEFT, padx=5)

        self.stealth_var = BooleanVar()
        Checkbutton(btn_frame, text="Stealth Mode", variable=self.stealth_var).pack(side=LEFT)

        Label(bottom, text="💖 Donate: buymeacoffee.com/rpetras", fg="white", bg="#111").pack()

    def load_category(self, category):
        for widget in self.tools_frame.winfo_children():
            widget.destroy()

        for tool, desc in TOOLS[category].items():
            var = BooleanVar()
            self.check_vars[tool] = var

            frame = Frame(self.tools_frame, bg="#0a0a0a")
            frame.pack(anchor="w")

            Checkbutton(frame, text=f"{tool} - {desc}",
                        variable=var, fg="#0f0", bg="#0a0a0a").pack(anchor="w")

    def get_selected(self):
        return [tool for tool, var in self.check_vars.items() if var.get()]

    def start_install(self):
        tools = self.get_selected()
        if not tools:
            messagebox.showwarning("Warning", "Select at least one tool")
            return

        threading.Thread(target=install_selected,
                         args=(tools, self.log, self.progress, self.stealth_var.get())).start()

    def install_full(self):
        all_tools = []
        for cat in TOOLS.values():
            all_tools.extend(cat.keys())

        threading.Thread(target=install_selected,
                         args=(all_tools, self.log, self.progress, self.stealth_var.get())).start()

    def update_tool(self):
        try:
            subprocess.run(["git", "-C", INSTALL_DIR, "pull"])
            messagebox.showinfo("Update", "Updated successfully!")
        except:
            messagebox.showerror("Error", "Update failed")

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    if os.geteuid() == 0:
        print("⚠️ Do not run as root. Use sudo internally.")
        sys.exit()

    root = Tk()
    app = App(root)
    root.mainloop()
