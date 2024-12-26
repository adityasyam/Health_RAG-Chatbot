import pytest
from conversation import query_follow_up_questions

#THIS FILE HAS UNIT TESTS TO TEST THE QUERY FOLLOW UP FUNCTION FOR CONVERSATIONAL AI
#verifying that function handles a valid query
def test_valid_input():
    query = "Does the patient have a fever?"
    questions = query_follow_up_questions(query)
    assert isinstance(questions, list)
#verify functionality with another valid query
def test_valid_input_2():
    query = "Does the patient have any other symptoms?"
    questions = query_follow_up_questions(query)
    assert isinstance(questions, list)
#verifying behavior when the input query indicates end of conversation
def test_no_follow_up_questions():
    query = "End of conversation."
    questions = query_follow_up_questions(query)
    assert questions == []
#verifying how the function handles unusual query
def test_unusual_query():
    query = "asdfghjkl"
    questions = query_follow_up_questions(query)
    assert questions == []
#verifying that relevant follow-up questions are generated
def test_follow_up_questions():
    query = "What should I do if I have diabetes?"
    questions = query_follow_up_questions(query)
    assert isinstance(questions, list)
    assert len(questions) > 0
