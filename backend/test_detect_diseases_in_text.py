import pytest
from conversation import detect_diseases_in_text

#THIS FILE HAS UNIT TESTS TO TEST THE DETECT DISEASES IN TEXT FUNCTION FOR CONVERSATIONAL AI

# Checking for disease when present in the text
def test_diseases_in_text():
    text = "The patient has Diabetes and Asthma."
    diseases = detect_diseases_in_text(text)
    assert diseases == ["diabetes", "asthma"]

# Checking for disease when absent in the text
def test_no_diseases_in_text():
    text = "The patient is healthy and shows no signs of illness."
    diseases = detect_diseases_in_text(text)
    assert diseases == []

# Checking for disease is only partially in the text
def test_partial_matches():
    text = "The patient shows signs of diabetics."
    diseases = detect_diseases_in_text(text)
    assert diseases == []
    
def test_diseases_with_punctuation():
    # Punctuation-separated diseases
    text = "Diabetes; Asthma. Bipolar disorder: detected!"
    diseases = detect_diseases_in_text(text)
    expected = ["diabetes", "asthma", "bipolar disorder"]
    assert set(diseases) == set(expected), f"Expected {expected}, but got {diseases}"

# Checking casing distortions of diseases in text
def test_mixed_casing():
    text = "The patient has dIaBeTeS and aStHmA."
    diseases = detect_diseases_in_text(text)
    assert diseases == ["diabetes", "asthma"]

# Checking for a huge set of text
def test_large_text():
    text = " ".join(["The patient has Diabetes."] * 1000)
    diseases = detect_diseases_in_text(text)
    assert diseases == ["diabetes"]

