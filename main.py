import os
import subprocess
import webbrowser

# --- Configuratie ---
HTML_FILE = "index.html"
TARGET_RESOLUTION = "2560,1080" # Breedte,Hoogte

# Pad naar Chromium executable (pas aan indien nodig voor jouw systeem)
# Voor Raspberry Pi OS is dit meestal '/usr/bin/chromium-browser'
# Voor Windows, kun je het pad naar chrome.exe opgeven, bijv. 'C:/Program Files/Google/Chrome/Application/chrome.exe'
# Voor macOS, bijv. '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CHROMIUM_PATHS = [
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
]

def find_chromium():
    """Zoekt naar een bestaand Chromium/Chrome executable."""
    for path in CHROMIUM_PATHS:
        if os.path.exists(path):
            return path
    return None

def main():
    html_file_path = os.path.abspath(HTML_FILE)

    if not os.path.exists(html_file_path):
        print(f"Error: {HTML_FILE} niet gevonden op {html_file_path}")
        print("Zorg ervoor dat index.html in dezelfde map staat als dit script.")
        return

    chromium_executable = find_chromium()

    if chromium_executable:
        print(f"Chromium gevonden op: {chromium_executable}")
        # Commando voor kiosk modus met specifieke resolutie
        # --window-size en --window-position zijn wellicht niet altijd perfect op alle systemen/window managers
        # --force-device-scale-factor=1 kan helpen bij HiDPI schermen indien nodig
        cmd = [
            chromium_executable,
            f"--window-size={TARGET_RESOLUTION}",
            f"--window-position=0,0",
            "--kiosk",
            # "--incognito", # Optioneel: start in incognito modus
            # "--disable-pinch", # Optioneel: voorkom zoomen met touch
            # "--overscroll-history-navigation=0", # Optioneel: voorkom swipe navigatie
            # "--disable-features=TranslateUI", # Optioneel: verberg "pagina vertalen" pop-up
            f'file:///{html_file_path}'
        ]
        print(f"Starten van Chromium met commando: {' '.join(cmd)}")
        try:
            subprocess.Popen(cmd)
            print(f"{HTML_FILE} zou nu moeten openen in Chromium in kiosk modus.")
            print(f"Resolutie ingesteld op: {TARGET_RESOLUTION}")
            print("Druk op ALT+F4 (of equivalente toetscombinatie voor jouw OS) om de kiosk modus te sluiten.")
        except Exception as e:
            print(f"Fout bij het starten van Chromium: {e}")
            print("Probeer het handmatig te openen of open index.html in je standaard browser.")
            webbrowser.open(f'file:///{html_file_path}')
    else:
        print("Chromium/Chrome niet gevonden op de standaardlocaties.")
        print(f"Probeer {HTML_FILE} handmatig te openen in je browser.")
        webbrowser.open(f'file:///{html_file_path}')

if __name__ == "__main__":
    main() 