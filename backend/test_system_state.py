import pytest
from conversation import conversation_state, generate_chat_response

#THIS FILE HAS UNIT TESTS TO TEST THE SYSTEM STATE FOR CONVERSATIONAL AI
#verifies that question count inrements correctly in the conversation state
def test_question_count_increments():
    initial_count = conversation_state["questions_asked"]
    generate_chat_response("What are common symptoms of a cold?")
    assert conversation_state["questions_asked"] == initial_count + 1
#verifies that question count increments correctly for another question
def test_question_count_increments_2():
    initial_count = conversation_state["questions_asked"]
    generate_chat_response("Tell me about yoga")
    assert conversation_state["questions_asked"] == initial_count + 1
#verifies that the "enough context" flag toggles as expected
def test_enough_context_toggles():
    for _ in range(5):
        generate_chat_response("Dummy query which means nothing")
    assert conversation_state["enough_context"] is False
