# Hydra Discord Nitro Sniper

![Hydra Banner](https://i.imgur.com/K2cQRhZ.png)

Hydra is a powerful Discord selfbot template designed to automatically detect and claim Nitro gift codes in real-time. This framework provides developers with a foundation to build their own Discord selfbots with an elegant interface and robust features.

## 🔍 How It Works

Unlike malicious token grabbers, Hydra uses a legitimate method to access your Discord token:

1. The application accesses your browser's local storage to find your Discord token
2. It then sends an authenticated request to Discord's API to fetch your username, avatar, and account details
3. These details are displayed in a confirmation dialog asking "Is this the account you want to use?"
4. Only after confirmation will the selfbot load and connect to Discord

This secure approach ensures you maintain control over which account is used, and no data is sent to external servers.

## ⚡ Features

- **Selfbot Template:** Build your own custom Discord selfbot on top of this framework
- **Automatic Nitro Code Detection:** Scans all messages across your servers for valid Discord Nitro gift links
- **Ultra-Fast Claiming:** Responds to gift codes in milliseconds to maximize your chances
- **Beautiful UI:** Modern Discord-inspired interface with visual feedback
- **Account Verification:** Secure account detection and confirmation dialog
- **Comprehensive Logging:** Keeps detailed logs of detected codes, claims, and activities
- **Customizable Experience:** Configurable settings to match your preferences

## 📸 Screenshots

<div align="center">
  <img src="https://i.imgur.com/913oCar.png" alt="ss1" width="400">
  <img src="https://i.imgur.com/hcn3kEx.png" alt="ss2" width="400">
</div>

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Discord account
- Required Python packages (see below)

### Steps

1. **Clone the repository:**
   ```
    Install the .zip and unzip it
   ```

2. **Install dependencies:**
   ```
   run setup.bat
   ```

3. **Run the application:**
   ```
   run start.bat
   ```

### Required Packages

```
discord.py (1.7.3)
win32crypt
pycryptodome
requests
httpx
colorama
rich
pyperclip
PyQt5
```

## 🛠️ Usage

1. **Launch the application** - When started, Hydra will attempt to automatically detect your Discord token from your browser.
2. **Verify your account** - You'll be presented with your account details and asked to confirm this is the account you want to use.
3. **Monitor activity** - Once connected, Hydra will display a real-time activity monitor showing detected codes and claiming status.
4. **Use commands** - Type `!help` in Discord to view available commands.
5. **Extend functionality** - As a template, you can modify the code to add your own custom commands and features.

## 📊 Logging

Hydra automatically creates and maintains the following logs:

- `startup.log` - Records when the bot starts
- `nitro_attempts.log` - Records all detected Nitro codes and their outcomes
- `nitro_success.log` - Records successfully claimed Nitro gifts
- `commands.log` - Tracks all commands used
- `connection.log` - Monitors connection status
- `errors.log` - Records any errors encountered
- `crash.log` - Detailed crash reports if something goes wrong

## 🔧 Development

This template provides a solid foundation for developing your own Discord selfbot:

- Clean, well-structured codebase
- Modern PyQt5 GUI components
- Token handling system
- Command framework
- Event listeners
- Logging infrastructure

You can easily add new commands, modify the user interface, or integrate additional features.

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK**

- Selfbots violate Discord's Terms of Service
- This software is provided for educational purposes only
- The author takes no responsibility for any consequences resulting from the use of this tool
- Your Discord account may be banned if detected using automated tools
- I am not responsibile for any harm done by this tool.

## 🛡️ Safety Tips

- Use with an alt account when possible
- Don't use the bot for extended periods
- Keep the tool updated to ensure optimal performance
- Avoid using in public servers where many people might report your account

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔧 Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

---

<p align="center">
  <i>Made with ❤️ by Rescore | github.com/rescore09</i>
</p>
