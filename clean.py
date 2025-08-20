import pandas as pd
import re

def clean_sentence(sentence):
    # Replace "na" with "to"
    cleaned = re.sub(r'\bna\b', 'to', sentence)
    
    # Fix spaces before punctuation and after dollar signs
    cleaned = re.sub(r'\s+([.,!?])', r'\1', cleaned)
    cleaned = re.sub(r'\$\s+', '$', cleaned)
    
    # Remove specified brackets
    cleaned = re.sub(r'\s*-LRB-|-RRB-|-LCB-|-RCB-\s*', '', cleaned)
    
    # Fix capitalization for all-caps words
    def fix_caps(match):
        word = match.group(0)
        # If it's at the start of the sentence, use Title case
        if cleaned.index(word) == 0:
            return word.capitalize()
        # Otherwise use lowercase
        return word.lower()

    cleaned = cleaned.replace(" n't", "n't")
    cleaned = cleaned.replace(" 'll", "'ll")
    cleaned = cleaned.replace(" 's", "'s")
    
    cleaned = re.sub(r'\b[A-Z]{2,}\b', fix_caps, cleaned)
    
    # Fix incorrect articles
    cleaned = re.sub(r'\ban\s+([^aeiouAEIOU])', r'a \1', cleaned)
    
    return cleaned

def process_csv(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Clean the sentences3 4
    df['Original Sentence'] = df['Original Sentence'].apply(clean_sentence)
    df['New Sentence'] = df['New Sentence'].apply(clean_sentence)
    
    # Write to new CSV file
    df.to_csv(output_file, index=False)