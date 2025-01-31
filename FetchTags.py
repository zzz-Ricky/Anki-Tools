import requests
import json
import concurrent.futures
import time
from tqdm import tqdm
from rich.console import Console

# AnkiConnect URL
ANKI_CONNECT_URL = "http://localhost:8765"

# Your deck name
DECK_NAME = "Personal word bank"

# Field names
WORD_FIELD = "Front"      # The field where the Japanese word is stored
TYPE_FIELD = "Tags"  # The field where we will store the word type

# Console for refreshing CLI
console = Console()

def get_notes_from_deck(deck_name):
    """Retrieve note IDs from a given deck."""
    payload = {
        "action": "findNotes",
        "version": 6,
        "params": {"query": f'deck:"{deck_name}"'}
    }
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("result", [])
    except requests.RequestException as e:
        print(f"Error fetching notes from deck: {e}")
        return []


def get_note_info(note_ids):
    """Retrieve note info including fields."""
    payload = {
        "action": "notesInfo",
        "version": 6,
        "params": {"notes": note_ids}
    }
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("result", [])
    except requests.RequestException as e:
        print(f"Error fetching note info: {e}")
        return []


def get_word_type(word, progress_bar):
    """Fetch word type from Jisho.org API."""
    url = f"https://jisho.org/api/v1/search/words?keyword={word}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        result = response.json()

        # Extract part of speech if available
        if result["data"]:
            senses = result["data"][0].get("senses", [])
            if senses:
                return ", ".join(senses[0].get("parts_of_speech", []))  # Get first part of speech

        return "Unknown"  # If not found
    except requests.RequestException as e:
        if response.status_code == 429:
            progress_bar.set_description(f"Rate limit exceeded. Sleeping for a while before retrying...")
            time.sleep(5)  # Sleep for 5 seconds before retrying
            return get_word_type(word, progress_bar)  # Retry fetching the word type
        print(f"Error fetching word type from Jisho.org: {e}")
        return "Unknown"


def update_word_type(note_id, word_type):
    """Update the 'Word Type' field in Anki and return the status of the update."""
    payload = {
        "action": "updateNoteFields",
        "version": 6,
        "params": {
            "note": {
                "id": note_id,
                "fields": {
                    TYPE_FIELD: word_type
                }
            }
        }
    }
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        response.raise_for_status()
        result = response.json()

        # Check for success or failure based on the response
        if result.get("error") is None:
            return True
        else:
            print(f"Failed to update note {note_id}: {result.get('error')}")
            return False
    except requests.RequestException as e:
        print(f"Error updating word type in Anki: {e}")
        return False


def process_note_with_progress(note, progress_bar):
    """Process a single note, fetch word type, update Anki, and update the progress bar status."""
    word = note["fields"].get(WORD_FIELD, {}).get("value", "").strip()
    if not word:
        return

    word_type = get_word_type(word, progress_bar)
    update_word_type(note["noteId"], word_type)

    progress_bar.set_description(f"Processing: {word} -> {word_type}")
    progress_bar.update(1)


def main():
    print("Fetching cards from Anki...")
    note_ids = get_notes_from_deck(DECK_NAME)
    if not note_ids:
        print("No cards found.")
        return

    notes = get_note_info(note_ids)

    console.print("Processing notes...")

    with tqdm(total=len(notes), desc="Processing notes") as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_note_with_progress, note, progress_bar) for note in notes]

            for future in concurrent.futures.as_completed(futures):
                future.result()  # Ensure all tasks are completed

    print("✅ Word type update complete!")


if __name__ == "__main__":
    main()
