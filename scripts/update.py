#!/usr/bin/env python3

import json
import re
import requests
import sys
from typing import Dict, List, Optional

# Configuration
ANKI_CONNECT_URL = "http://localhost:8765"
DECK_NAME = "GRE Vocabulary"
CAMBRIDGE_API_URL = "https://dict.meowrain.cn/api/dictionary/en-cn/"

def check_anki_connect() -> bool:
    """Check if AnkiConnect is available and running."""
    try:
        response = requests.post(ANKI_CONNECT_URL, json={
            "action": "version",
            "version": 6
        })
        return response.ok
    except requests.exceptions.RequestException:
        return False

def get_deck_names() -> List[str]:
    """Get all deck names from Anki."""
    response = requests.post(ANKI_CONNECT_URL, json={
        "action": "deckNames",
        "version": 6
    })
    if response.ok:
        return response.json()["result"]
    return []

def get_cambridge_definition(word: str) -> Optional[Dict]:
    """Get word definition from Cambridge Dictionary API."""
    try:
        response = requests.get(f"{CAMBRIDGE_API_URL}{word}")
        if response.ok:
            return response.json()
        else:
            print(f"Warning: Failed to get definition for word '{word}'. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Warning: API request failed for word '{word}': {str(e)}")
        return None

def format_definition(word: str, api_response: Optional[Dict]) -> Optional[str]:
    """Format the definition according to the specified template. Returns None if no valid definitions found."""
    if not api_response:
        return None
    
    # Initialize sections for each part of speech
    sections = {
        "Verb": [],
        "Noun": [],
        "Adjective": [],
        "Adverb": []
    }
    
    # Map API's pos to our categories
    pos_mapping = {
        "verb": "Verb",
        "noun": "Noun",
        "adjective": "Adjective",
        "adverb": "Adverb"
    }
    
    # Process definitions
    has_valid_definitions = False
    for entry in api_response.get("definition", []):
        pos = entry.get("pos", "").lower()
        if pos in pos_mapping:
            category = pos_mapping[pos]
            definition = entry.get("text", "").strip()
            examples = [ex.get("text", "") for ex in entry.get("example", [])]
            if definition:  # Only add if there's a definition
                has_valid_definitions = True
                sections[category].append({
                    "definition": definition,
                    "examples": examples
                })
    
    if not has_valid_definitions:
        return None

    # Format the output with HTML
    output = ["<hr><div><b>Definitions:</b></div>"]
    
    for idx, (pos, definitions) in enumerate(sections.items(), 1):
        if not definitions:  # Skip empty sections
            continue
            
        # Add the part of speech header
        output.append(f"\n<div>{idx}. <b>{pos}:</b></div>")
        
        # Add each definition with its examples
        for def_idx, def_data in enumerate(definitions, 1):
            output.append(f"<div style='margin-left: 20px'>{def_idx}. {def_data['definition']}</div>")
            if def_data['examples']:
                output.append("<div style='margin-left: 40px'><i>Examples:</i></div>")
                for ex_idx, example in enumerate(def_data['examples'], 1):
                    output.append(f"<div style='margin-left: 40px'>{ex_idx}. {example}</div>")
        
        # Add sentences and synonyms sections
        output.append("<div style='margin-left: 20px'>- Sentences:</div>")
        output.append("<div style='margin-left: 20px'>- Synonyms:</div>")
    
    return "\n".join(output)

def get_cards_to_update() -> List[Dict]:
    """Get all cards from the deck that need updating."""
    # First, get all deck names and print them
    deck_names = get_deck_names()
    print("\nAvailable decks:")
    for deck in deck_names:
        print(f"- '{deck}'")
    print(f"\nLooking for deck: '{DECK_NAME}'")

    # Get all notes from the deck
    response = requests.post(ANKI_CONNECT_URL, json={
        "action": "findNotes",
        "version": 6,
        "params": {
            "query": f'deck:"{DECK_NAME}"'
        }
    })
    
    if not response.ok:
        print(f"Error response from findNotes: {response.text}")
        raise Exception("Failed to get notes from Anki")
    
    note_ids = response.json()["result"]
    print(f"\nFound {len(note_ids)} total notes in the deck")
    
    if not note_ids:
        return []

    # Get note info
    response = requests.post(ANKI_CONNECT_URL, json={
        "action": "notesInfo",
        "version": 6,
        "params": {
            "notes": note_ids
        }
    })
    
    if not response.ok:
        print(f"Error response from notesInfo: {response.text}")
        raise Exception("Failed to get note information")
        
    notes = response.json()["result"]
    
    # Print first note fields for debugging
    if notes:
        print("\nFirst note fields:")
        for field_name, field_data in notes[0]["fields"].items():
            print(f"- {field_name}: {field_data['value'][:50]}...")
    
    # Filter notes that don't already have the desired format
    pattern = re.compile(r".*Definitions:.*", re.DOTALL)
    filtered_notes = [note for note in notes if not pattern.match(note["fields"]["Details"]["value"])]
    
    print(f"\nFiltered to {len(filtered_notes)} notes that need updating")
    return filtered_notes

def update_card(note_id: int, existing_content: str, new_content: str) -> bool:
    """Update a single card by appending new content to existing content."""
    response = requests.post(ANKI_CONNECT_URL, json={
        "action": "updateNoteFields",
        "version": 6,
        "params": {
            "note": {
                "id": note_id,
                "fields": {
                    "Details": existing_content + new_content
                }
            }
        }
    })
    return response.ok

def main():
    """Main function to run the update process."""
    if not check_anki_connect():
        print("Error: Cannot connect to Anki. Please make sure Anki is running and AnkiConnect is installed.")
        sys.exit(1)
    
    try:
        cards = get_cards_to_update()
        total_cards = len(cards)
        print(f"Found {total_cards} cards to update")
        
        success_count = 0
        skip_count = 0
        for idx, card in enumerate(cards, 1):
            word = card["fields"]["Word"]["value"]
            print(f"Processing word {idx}/{total_cards}: {word}")
            
            definitions = get_cambridge_definition(word)
            new_content = format_definition(word, definitions)
            
            if new_content is None:
                print(f"⚠ Skipping word '{word}' - no valid definitions found")
                skip_count += 1
                continue
                
            existing_content = card["fields"]["Details"]["value"]
            success = update_card(card["noteId"], existing_content, new_content)
            
            if success:
                success_count += 1
                print(f"✓ Successfully updated card for word: {word}")
            else:
                print(f"✗ Failed to update card for word: {word}")
            
        print(f"\nUpdate complete!")
        print(f"- Successfully updated: {success_count} cards")
        print(f"- Skipped (no definitions): {skip_count} cards")
        print(f"- Total processed: {total_cards} cards")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
