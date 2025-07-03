import os
import shutil
from datetime import datetime
from PIL import Image
from tqdm import tqdm

def get_exif_date(image_path):
    """
    Tenta di ottenere la data di scatto dai metadati EXIF dell'immagine.
    Se non presente, tenta di usare la data di modifica del file.
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                date_str = exif_data.get(36867) or exif_data.get(36868) or exif_data.get(306)
                if date_str:
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        pass # Non stampiamo qui per non intasare l'output

    # Fallback: Se la data EXIF non è disponibile, usa la data di modifica del file
    try:
        timestamp = os.path.getmtime(image_path)
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        return None

def organize_photos_in_current_folder():
    """
    Organizza le foto nella cartella corrente in sottocartelle basate sulla data di scatto.
    Chiede all'utente dove creare la cartella "FotoOrganizzate".
    """
    source_folder = os.getcwd()

    # Chiedi all'utente il percorso di destinazione
    user_input = input(
        "Inserisci il percorso dove creare la cartella 'FotoOrganizzate' (premi Invio per usare la cartella corrente):\n> "
    ).strip()
    if user_input:
        destination_base_folder = os.path.join(user_input, "FotoOrganizzate")
    else:
        destination_base_folder = os.path.join(source_folder, "FotoOrganizzate")

    print(f"La cartella di origine è: '{source_folder}'")
    print(f"Le foto organizzate verranno spostate in: '{destination_base_folder}'")
    print("-" * 50) # Linea separatrice per chiarezza

    # Prepara la lista dei file immagine da elaborare
    image_files = []
    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)
        # Assicurati di non includere la cartella di destinazione stessa o lo script
        if os.path.isfile(file_path) and \
            filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg', '.mp4', '.mkv', '.avi', 'mov')) and \
            file_path != os.path.join(source_folder, os.path.basename(__file__)): # Evita di elaborare lo script stesso
            image_files.append(filename)

    if not image_files:
        print(f"Nessuna immagine supportata trovata nella cartella '{source_folder}'.")
        print("Assicurati che lo script si trovi nella cartella corretta e che ci siano immagini.")
        return

    # Crea la cartella di destinazione base se non esiste
    os.makedirs(destination_base_folder, exist_ok=True)
    print(f"Inizio organizzazione delle {len(image_files)} foto...")

    # Usa tqdm per avvolgere l'iterazione sui file con una barra di progresso
    for filename in tqdm(image_files, desc="Organizzazione immagini", unit="foto"):
        file_path = os.path.join(source_folder, filename)

        photo_date = get_exif_date(file_path)

        if photo_date:
            date_folder_name = photo_date.strftime('%Y-%m-%d')
            destination_folder = os.path.join(destination_base_folder, date_folder_name)

            # Crea la cartella di destinazione per la data specifica se non esiste
            os.makedirs(destination_folder, exist_ok=True)

            # Sposta il file
            try:
                shutil.move(file_path, os.path.join(destination_folder, filename))
                tqdm.write(f"  [OK] '{filename}' spostato in '{date_folder_name}'")
            except Exception as e:
                tqdm.write(f"  [ERRORE] Impossibile spostare '{filename}': {e}")
        else:
            tqdm.write(f"  [ATTENZIONE] Impossibile determinare la data per '{filename}'. Saltato.")

    print("\nOrganizzazione completata!")
    print(f"Le foto sono state spostate in '{destination_base_folder}'.")

if __name__ == '__main__':
    organize_photos_in_current_folder()