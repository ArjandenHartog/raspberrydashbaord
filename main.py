import os
import subprocess
import webbrowser
import platform

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

def disable_screen_blanking():
    """Schakelt schermbeveiliging en energiebeheer uit op Raspberry Pi."""
    if platform.system() == "Linux":
        try:
            # Schakel DPMS (energiebeheer) uit
            subprocess.run(['xset', '-dpms'], check=True)
            # Schakel screensaver uit
            subprocess.run(['xset', 's', 'off'], check=True)
            # Schakel screen blanking uit
            subprocess.run(['xset', 's', 'noblank'], check=True)
            print("Schermbeveiliging en energiebeheer uitgeschakeld")
            
            # Voeg de instellingen toe aan /etc/xdg/lxsession/LXDE-pi/autostart voor persistentie
            autostart_path = "/etc/xdg/lxsession/LXDE-pi/autostart"
            if os.path.exists(autostart_path):
                try:
                    with open(autostart_path, 'a') as f:
                        f.write("\n@xset s off\n@xset -dpms\n@xset s noblank\n")
                    print("Instellingen toegevoegd aan autostart")
                except PermissionError:
                    print("Let op: Kon autostart niet aanpassen. Voer het script uit met sudo voor permanente instellingen.")
        except subprocess.CalledProcessError as e:
            print(f"Waarschuwing: Kon schermbeveiliging niet uitschakelen: {e}")
        except FileNotFoundError:
            print("Waarschuwing: xset commando niet gevonden. Is X11 geïnstalleerd?")

def find_chromium():
    """Zoekt naar een bestaand Chromium/Chrome executable."""
    for path in CHROMIUM_PATHS:
        if os.path.exists(path):
            return path
    return None

def main():
    # Schakel eerst schermbeveiliging uit
    disable_screen_blanking()
    
    html_file_path = os.path.abspath(HTML_FILE)

    if not os.path.exists(html_file_path):
        print(f"Error: {HTML_FILE} niet gevonden op {html_file_path}")
        print("Zorg ervoor dat index.html in dezelfde map staat als dit script.")
        return

    chromium_executable = find_chromium()

    if chromium_executable:
        print(f"Chromium gevonden op: {chromium_executable}")
        # Commando voor kiosk modus met specifieke resolutie
        cmd = [
            chromium_executable,
            "--start-fullscreen",  # Force fullscreen
            "--kiosk",  # Kiosk mode
            "--noerrdialogs",  # Voorkom error dialogs
            "--disable-translate",  # Schakel vertaal popup uit
            "--disable-features=TranslateUI",  # Schakel vertaal UI uit
            "--disable-pinch",  # Voorkom zoomen met touch/trackpad
            "--overscroll-history-navigation=0",  # Voorkom swipe navigatie
            "--disable-infobars",  # Verberg infobars
            "--check-for-update-interval=31536000",  # Check voor updates maar 1x per jaar
            f"--window-size={TARGET_RESOLUTION}",
            f"--window-position=0,0",
            f'file:///{html_file_path}'
        ]
        print(f"Starten van Chromium met commando: {' '.join(cmd)}")
        try:
            # Start Chromium en wacht niet op het proces (non-blocking)
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