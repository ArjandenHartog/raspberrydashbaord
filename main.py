import os
import subprocess
import webbrowser
import platform
import sys
import time

# --- Configuratie ---
HTML_FILE = "index.html"
TARGET_RESOLUTION = "2560,1080" # Breedte,Hoogte
DEBUG = True  # Debug modus aan

# Pad naar Chromium executable (pas aan indien nodig voor jouw systeem)
# Voor Raspberry Pi OS is dit meestal '/usr/bin/chromium-browser'
# Voor Windows, kun je het pad naar chrome.exe opgeven, bijv. 'C:/Program Files/Google/Chrome/Application/chrome.exe'
# Voor macOS, bijv. '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CHROMIUM_PATHS = [
    # Raspberry Pi / Linux paths
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser-stable',
    '/snap/bin/chromium',
    # Windows paths
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    # macOS path
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
]

def debug_print(message):
    """Print debug informatie als DEBUG aan staat."""
    if DEBUG:
        print(f"[DEBUG] {message}")

def is_root():
    """Check of het script als root draait."""
    return os.geteuid() == 0 if hasattr(os, 'geteuid') else False

def check_system_info():
    """Controleer en print systeem informatie voor debugging."""
    debug_print(f"Besturingssysteem: {platform.system()} {platform.release()}")
    debug_print(f"Python versie: {sys.version}")
    debug_print(f"Werkmap: {os.getcwd()}")
    debug_print(f"Draait als root: {is_root()}")
    
    # Check DISPLAY variabele op Linux
    if platform.system() == "Linux":
        display = os.environ.get('DISPLAY')
        debug_print(f"DISPLAY environment: {display}")
        
        # Check of we in een GUI sessie zitten
        desktop_session = os.environ.get('DESKTOP_SESSION')
        debug_print(f"Desktop sessie: {desktop_session}")

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
            debug_print("Schermbeveiliging en energiebeheer uitgeschakeld")
            
            # Voeg de instellingen toe aan /etc/xdg/lxsession/LXDE-pi/autostart voor persistentie
            autostart_path = "/etc/xdg/lxsession/LXDE-pi/autostart"
            if os.path.exists(autostart_path):
                try:
                    with open(autostart_path, 'a') as f:
                        f.write("\n@xset s off\n@xset -dpms\n@xset s noblank\n")
                    debug_print("Instellingen toegevoegd aan autostart")
                except PermissionError:
                    debug_print("Let op: Kon autostart niet aanpassen. Voer het script uit met sudo voor permanente instellingen.")
        except subprocess.CalledProcessError as e:
            debug_print(f"Waarschuwing: Kon schermbeveiliging niet uitschakelen: {e}")
        except FileNotFoundError:
            debug_print("Waarschuwing: xset commando niet gevonden. Is X11 geïnstalleerd?")

def find_chromium():
    """Zoekt naar een bestaand Chromium/Chrome executable."""
    debug_print("Zoeken naar Chromium/Chrome executable...")
    for path in CHROMIUM_PATHS:
        debug_print(f"Controleren: {path}")
        if os.path.exists(path):
            debug_print(f"Gevonden: {path}")
            return path
    debug_print("Geen Chromium/Chrome executable gevonden in standaard locaties")
    return None

def get_chromium_flags():
    """Bepaal de juiste flags voor Chromium gebaseerd op de uitvoeringscontext."""
    flags = [
        "--start-fullscreen",  # Force fullscreen
        "--kiosk",  # Kiosk mode
        "--noerrdialogs",  # Voorkom error dialogs
        "--disable-translate",  # Schakel vertaal popup uit
        "--disable-features=TranslateUI",  # Schakel vertaal UI uit
        "--disable-pinch",  # Voorkom zoomen met touch/trackpad
        "--overscroll-history-navigation=0",  # Voorkom swipe navigatie
        "--disable-infobars",  # Verberg infobars
        "--check-for-update-interval=31536000",  # Check voor updates maar 1x per jaar
    ]
    
    # Als we als root draaien, voeg de nodige sandbox flags toe
    if is_root():
        flags.extend([
            "--no-sandbox",
            "--disable-setuid-sandbox"
        ])
    
    return flags

def try_alternative_chromium_start(html_file_path):
    """Probeer alternatieve manieren om Chromium te starten."""
    debug_print("Proberen alternatieve manieren om Chromium te starten...")
    
    flags = get_chromium_flags()
    flags_str = " ".join(flags)
    
    try:
        # Methode 1: Via shell command met alle flags
        cmd = f"DISPLAY=:0 chromium-browser {flags_str} '{html_file_path}'"
        debug_print(f"Probeer methode 1: {cmd}")
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception as e:
        debug_print(f"Methode 1 gefaald: {e}")
    
    try:
        # Methode 2: Direct command zonder shell
        cmd = ["chromium-browser"] + flags + [html_file_path]
        debug_print(f"Probeer methode 2: {' '.join(cmd)}")
        subprocess.Popen(cmd)
        return True
    except Exception as e:
        debug_print(f"Methode 2 gefaald: {e}")
    
    return False

def main():
    check_system_info()
    
    # Schakel eerst schermbeveiliging uit
    disable_screen_blanking()
    
    html_file_path = os.path.abspath(HTML_FILE)
    debug_print(f"HTML bestand pad: {html_file_path}")

    if not os.path.exists(html_file_path):
        print(f"Error: {HTML_FILE} niet gevonden op {html_file_path}")
        print("Zorg ervoor dat index.html in dezelfde map staat als dit script.")
        return

    chromium_executable = find_chromium()

    if chromium_executable:
        debug_print(f"Chromium gevonden op: {chromium_executable}")
        # Basiscommando met alle flags
        cmd = [chromium_executable] + get_chromium_flags()
        # Voeg resolutie en bestandspad toe
        cmd.extend([
            f"--window-size={TARGET_RESOLUTION}",
            f"--window-position=0,0",
            f'file:///{html_file_path}'
        ])
        
        debug_print(f"Starten van Chromium met commando: {' '.join(cmd)}")
        try:
            # Start Chromium en wacht niet op het proces (non-blocking)
            process = subprocess.Popen(cmd)
            debug_print(f"Chromium process ID: {process.pid}")
            time.sleep(2)  # Wacht even om te zien of het process blijft draaien
            
            if process.poll() is not None:  # Process is al gestopt
                debug_print("Chromium process stopte onverwacht, probeer alternatieve methode")
                if not try_alternative_chromium_start(html_file_path):
                    print("Kon Chromium niet starten met standaard of alternatieve methoden")
            else:
                print(f"{HTML_FILE} geopend in Chromium kiosk modus")
                print(f"Resolutie ingesteld op: {TARGET_RESOLUTION}")
                print("Druk op ALT+F4 (of equivalente toetscombinatie voor jouw OS) om de kiosk modus te sluiten.")
        except Exception as e:
            debug_print(f"Fout bij het starten van Chromium: {str(e)}")
            print("Probeer alternatieve methode...")
            if not try_alternative_chromium_start(html_file_path):
                print("Kon Chromium niet starten. Probeer het bestand handmatig te openen.")
                webbrowser.open(f'file:///{html_file_path}')
    else:
        print("Chromium/Chrome niet gevonden. Controleer of het is geïnstalleerd.")
        print("Op Raspberry Pi, installeer Chromium met:")
        print("sudo apt update && sudo apt install -y chromium-browser")
        
        response = input("Wil je het bestand in de standaard browser openen? (ja/nee): ")
        if response.lower() in ['ja', 'j', 'yes', 'y']:
            webbrowser.open(f'file:///{html_file_path}')

if __name__ == "__main__":
    main() 