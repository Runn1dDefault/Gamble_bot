>:warning: **Required!** #!usr/bin/env python3.8
#### main file is GUI.py

## Manual to install Tesseract-OCR
Tesseract to perform text recognition

[Tesseract install](https://github.com/UB-Mannheim/tesseract/wiki)

----
## API
```text
In config.py:
- API_URL - Base API url   # http://185.151.31.66:8009/
- API_LOGS_URL - endpoint for saving logs 
- API_TOKEN_URL - endpoint for user authentication
- API_GAMBLE_SITES_URL - endpoint for getting sites for user
```
---
## Build exe for Windows
#### 1. Install pyinstaller
> pip install pyinstaller
#### 2. Change the hookspath in win.spec according to the example in it
#### 3. pyinstaller win.spec

---
## Build app for MacOS
#### 1. Install pyinstaller
> pip install pyinstaller
#### 2. pyinstaller GambleBot.spec

---


