import pandas as pd
import genanki
import os
import random

# Create a unique model ID
model_id = random.randrange(1 << 30, 1 << 31)

# Define the Anki note model (template)
gre_model = genanki.Model(
    model_id,
    "GRE Vocabulary Model",
    fields=[
        {"name": "Word"},
        {"name": "Details"},
    ],
    templates=[
        {
            "name": "GRE Vocabulary Card",
            "qfmt": '<div style="font-size: 24px; text-align: center;">{{Word}}</div>',
            "afmt": '<div style="font-size: 24px; text-align: center;">{{Word}}</div><hr><div>{{Details}}</div>',
        },
    ],
)

# Create a unique deck ID
deck_id = random.randrange(1 << 30, 1 << 31)

# Create a new deck
deck = genanki.Deck(deck_id, "GRE Vocabulary")

# Read the Excel file
df = pd.read_excel("data/3000.xlsx")

# Process each word and add to the deck
for _, row in df.iterrows():
    # Skip rows with missing Word
    if pd.isna(row["Word"]):
        continue

    # Create the answer string with all the additional information
    details = ""

    if not pd.isna(row["UK Phonetics"]):
        details += f"<div><b>UK Phonetics:</b> {row['UK Phonetics']}</div>"

    if not pd.isna(row["US Phonetics"]):
        details += f"<div><b>US Phonetics:</b> {row['US Phonetics']}</div>"

    if not pd.isna(row["Paraphrase"]):
        details += f"<div><b>Paraphrase:</b> {row['Paraphrase']}</div>"

    if not pd.isna(row["Paraphrase (w/ POS)"]):
        details += (
            f"<div><b>Paraphrase (w/ POS):</b> {row['Paraphrase (w/ POS)']}</div>"
        )

    if not pd.isna(row["Paraphrase (English)"]):
        details += (
            f"<div><b>Paraphrase (English):</b> {row['Paraphrase (English)']}</div>"
        )

    # Create a note and add it to the deck
    note = genanki.Note(model=gre_model, fields=[str(row["Word"]), details])
    deck.add_note(note)

# Create output directory if it doesn't exist
os.makedirs("out", exist_ok=True)

# Generate and save the Anki deck package
package = genanki.Package(deck)
package.write_to_file("out/gre_vocabulary.apkg")

print(
    f"Successfully created Anki deck with {len(deck.notes)} cards in out/gre_vocabulary.apkg"
)
