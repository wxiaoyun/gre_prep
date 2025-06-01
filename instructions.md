Task: I have an anki deck with flask cards on GRE vocabulary.
The questions are the vocab and the answers are the definitions. However I have a lot of cards that contain definitions that are not in the format I want.

Your task is to create a python script that will make use of anki-connect to retrieve the cards and format them to the following format:

---Start of format---
Definitions:

1. Verb: <definition_1>
   1. Sentences: 
   2. Synonyms: 

2. Noun: <definition_2>
   1. Sentences: 
   2. Synonyms: 

3. Adjective: <definition_3>
   1. Sentences: 
   2. Synonyms: 

4. Adverb: <definition_4>
   1. Sentences: 
   2. Synonyms: 
---End of format---

Here are the requirements:
- The exported deck is in "./data/GRE_Vocabulary.apkg"
- The modifications should not be destructive and it must perserve the scheduling information of the deck. It should strictly modity the flashcard content/answer.
- There are some cards that are already in the format I want. These cards should not be modified. You can check for this by looking at the answer field with the following regex: 
  - `.*Definitions:.*`
- You should be use the cambridge dictionary api to get the definitions.

Make any clarifications you need.