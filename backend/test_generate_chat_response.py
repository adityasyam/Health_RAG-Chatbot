import pytest
from conversation import generate_chat_response, conversation_state

#THIS FILE HAS UNIT TESTS TO TEST THE GENERATE CHAT RESPONSE FUNCTION FOR CONVERSATIONAL AI
#checks if the system can handle a simple generic query
def test_generic_query():
    query = "What are the symptoms of flu?"
    response = generate_chat_response(query)
    assert "symptoms" in response.lower()
#checks that the conversation AI considers patient-specific context
def test_patient_context_query():
    from conversation import update_conversation_context
    data = {"patient_number": 123, "past_history": ["Diabetes"], "family_history": ["Heart Disease"]}
    update_conversation_context(data)

    query = "What precautions should the patient take?"
    response = generate_chat_response(query)
    assert "diabetes" in response.lower()
#testing handling of very long input queries
def test_long_input():
    query = "a" * 10000
    response = generate_chat_response(query)
    assert "error" in response.lower()
#verifiying that the no. of questions asked is tracked correctly    
def test_question_count_increments():
    initial_count = conversation_state["questions_asked"]
    generate_chat_response("Tell me about yoga")
    assert conversation_state["questions_asked"] == initial_count + 1
#verifying handling of long valid queries    
def test_long_query():
    query = "What are the health effects of smoking and how does it cause lung cancer? " * 50
    response = generate_chat_response(query)
    assert "error" not in response.lower()

