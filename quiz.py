#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 14:19:51 2024

@author: jhmueller

INSTRUCTIONS OF USE:
1. Install the numpy, pandas, requests, and random python modules
2. Go to www.dictionaryapi.com and get an API key.
3. Create a word list file: a .txt file with one word on each line.
"""

# Necessary modules
import numpy as np
import pandas as pd
import requests
import random

# Variables
#file_path = 'path/to/your/file.txt'  # File path of word list
file_path = 'Documents/word_list.txt'  # File path of word list
api_key = 'd1fb832d-d456-4a57-9e3e-4cb9917a5a6f' # API key

# Loads word list to numpy array
with open(file_path, 'r') as file:
    words = file.read().splitlines()
# Convert the list of words to a NumPy array
word_array = np.array(words, dtype=object) 

# Select 5 random elements of the word list
random_selection = np.random.choice(word_array, size=15, replace=False)

# Get word information from Merriam-Webster
colnames = ['Word', 'Etymology', 'Word Type', 'Definition']
mini_dictionary = pd.DataFrame(columns = colnames)
print("Downloading word information...")
for word in random_selection:
    response = requests.get("https://www.dictionaryapi.com/api/v3/references/collegiate/json/" + word + "?key=" + api_key)
    entry = response.json()
    try:
        down_word = entry[0]['meta']['id']
    except: 
        down_word = word
    try: 
        et = entry[0]['et'][0][1]
    except:
        et = 'NA'
    try: 
        w_type = entry[0]['fl']
    except: 
        w_type = 'ERROR: TYPO'
    try: 
        definition = str(entry[0]['shortdef'])
    except:
        definition = 'ERROR: TYPO'
    definition.replace(down_word, '________')
    mini_dictionary= pd.concat([mini_dictionary, pd.DataFrame({'Word': down_word, 'Etymology': et, 'Word Type': w_type, 'Definition':definition}, index = [0])], ignore_index = True)
    del down_word, et, w_type, definition
del word, random_selection

### GENERATE AND RUN THE QUIZ ###
def create_quiz(df, num_questions=3):
    questions = []
    answers = []
    etymologies = []
    word_types = []
    options_list = []
    used_words = set()
    used_definitions = set()
    
    # Questions about definitions
    for _ in range(num_questions):
        # Filter out already used words
        available_words = df[~df['Word'].isin(used_words)]['Word']
        if len(available_words) == 0:
            break
        
        word = random.choice(available_words.tolist())
        used_words.add(word)
        
        correct_def = df.loc[df['Word'] == word, 'Definition'].iloc[0]
        correct_etymology = df.loc[df['Word'] == word, 'Etymology'].iloc[0]
        correct_word_type = df.loc[df['Word'] == word, 'Word Type'].iloc[0]
        # Filter out already used definitions for incorrect options
        available_defs = df[~df['Definition'].isin(used_definitions | {correct_def})]['Definition']
        if len(available_defs) < 3:
            break
        
        incorrect_defs = available_defs.sample(3).tolist()
        options = [correct_def] + incorrect_defs
        random.shuffle(options)
        
        question = f"What is the definition of '{word}'?"
        questions.append(question)
        answers.append(options.index(correct_def))
        used_definitions.add(correct_def)
        used_definitions.update(incorrect_defs)
        options_list.append(options)
        etymologies.append(correct_etymology)
        word_types.append(correct_word_type)
    
    # Questions about words
    for _ in range(num_questions):
        # Filter out already used definitions
        available_defs = df[~df['Definition'].isin(used_definitions)]['Definition']
        if len(available_defs) == 0:
            break
        
        definition = random.choice(available_defs.tolist())
        used_definitions.add(definition)
        
        correct_word = df.loc[df['Definition'] == definition, 'Word'].iloc[0]
        correct_etymology = df.loc[df['Definition'] == definition, 'Etymology'].iloc[0]
        correct_word_type = df.loc[df['Definition'] == definition, 'Word Type'].iloc[0]
        # Filter out already used words for incorrect options
        available_words = df[~df['Word'].isin(used_words | {correct_word})]['Word']
        if len(available_words) < 3:
            break
        
        incorrect_words = available_words.sample(3).tolist()
        options = [correct_word] + incorrect_words
        random.shuffle(options)
        
        question = f"Which word matches this definition: '{definition}'?"
        questions.append(question)
        answers.append(options.index(correct_word))
        used_words.add(correct_word)
        used_words.update(incorrect_words)
        options_list.append(options)
        etymologies.append(correct_etymology)
        word_types.append(correct_word_type)
    
    return questions, answers, etymologies, word_types, options_list

def run_quiz(questions, answers, etymologies, word_types, options_list):
    score = 0
    for i, (question, options) in enumerate(zip(questions, options_list)):
        print(f"\nQuestion {i+1}: {question}")
        for j, option in enumerate(options):
            print(f"  {j+1}. {option}")
        
        user_answer = int(input("Enter the number of your answer: ")) - 1
        if user_answer == answers[i]:
            print("Correct!")
            print(etymologies[i])
            print(word_types[i])
            score += 1
        else:
            print(f"Sorry, that's incorrect. The correct answer was {answers[i] + 1}.")
            print(etymologies[i])
            print(word_types[i])
    
    print(f"\nYou scored {score} out of {len(questions)}!")

# Generate the quiz
questions, answers, etymologies, word_types, options_list = create_quiz(mini_dictionary)

# Run the quiz
run_quiz(questions, answers, etymologies, word_types, options_list)