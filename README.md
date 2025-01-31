# Anki Tools
This is a repository to store small anki related scripts to automate tedious tasks
## Anki Word Type Updater

This tool automatically fetches word types (verb, noun, etc) for words in your Japanese Anki deck and updates the "Tags" field in each card using the Jisho API. This might be useful if you also use Yomichan to Automate Card Creation and need to update old cards.

### Requirements
- Python 3.x
- `requests` library  
  Install with:  
  ```bash
  pip install requests
  ```
- `tqdm` library (for progress bars)  
  Install with:  
  ```bash
  pip install tqdm
  ```
- `rich` library (for enhanced console output)  
  Install with:  
  ```bash
  pip install rich
  ```
- AnkiConnect add-on installed and running in Anki (default port: 8765)

### Usage

1. **Set up the deck name**:  
   Modify the `DECK_NAME` variable to match the name of your deck in Anki where you want to update word types.

   ```python
   DECK_NAME = "Personal word bank"  # Replace with your deck's name
   ```

2. **Field customization**:  
   If you're using different field names for the word and type, modify these variables:
   
   - `WORD_FIELD`: The field where the word is stored (default: `"Front"`).
   - `TYPE_FIELD`: The field where the word type will be updated (default: `"Tags"`).

   ```python
   WORD_FIELD = "Front"  # Change to your word field name
   TYPE_FIELD = "Tags"   # Change to your desired field for word type
   ```

3. **Running the script**:
   Run the script with:
   
   ```bash
   python FetchTags.py
   ```

   The script will:
   - Fetch notes from the specified deck.
   - Get the word type for each word via the Jisho API.
   - Update the Anki cards with the fetched word type in the chosen field.

4. **Concurrency**:  
   The tool uses multi-threading to process multiple notes simultaneously. You can adjust the `max_workers` parameter in the `ThreadPoolExecutor` for the number of simultaneous requests. Though, this will have diminishing returns as you will be limited by the speed of your internet and access to the Jisho API.

### Notes

- Ensure AnkiConnect is running and accessible via `localhost:8765`.
- Jisho API is used to fetch word types; if the word is not found, it will default to "Unknown".
- This script will throttle in case you send too many requests to Jisho, you might need to wait a little to prevent accidentally DDOSing their APi
---
