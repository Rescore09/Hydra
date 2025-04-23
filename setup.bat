@echo off
echo Uninstalling discord.py...
pip uninstall -y discord.py

pip install discord.py==1.7.3

echo Installing packages from requirements.txt...
pip install -r requirements.txt

echo Done.
pause
