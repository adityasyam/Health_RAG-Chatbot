import pytest
from conversation import update_conversation_context

#THIS FILE HAS UNIT TESTS TO TEST THE CONVERSATION UPDATE FUNCTION FOR CONVERSATIONAL AI
#updating context with valid patient data
def test_valid_patient_data():
    data = {
        "patient_number": 123,
        "past_history": ["Diabetes", "Asthma"],
        "family_history": ["Heart Disease"]
    }
    current_context = update_conversation_context(data, test=True)
    assert current_context == data
#valid patient number but empty past and family history
def test_empty_patient_data():
    data = {
        "patient_number": 456,
        "past_history": [],
        "family_history": []
    }
    current_context = update_conversation_context(data, test=True)
    assert current_context == data
#try to update context with missing required keys
def test_missing_keys():
    data = {"patient_number": 789}
    with pytest.raises(KeyError):
        update_conversation_context(data)
#valid patient data and verifiying specific fields        
def test_valid_context():
    data = {"patient_number": 123, "past_history": ["Diabetes"], "family_history": ["Asthma"]}
    context = update_conversation_context(data, test=True)
    assert context["patient_number"] == 123
    assert "Diabetes" in context["past_history"]
#updating context with empty past and family history with a valid patient number
def test_empty_context():
    data = {"patient_number": 456, "past_history": [], "family_history": []}
    context = update_conversation_context(data, test=True)
    assert context == data
