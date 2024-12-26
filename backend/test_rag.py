import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from rag import app, main

#THIS FILE HAS UNIT TESTS FOR THE RAG.PY FILE

client = TestClient(app)

@pytest.fixture
def mock_env(mocker):
    """Mock environment variables."""
    mocker.patch("os.getenv", side_effect=lambda key: {
        "PINECONE_INDEX_NAME": "test_index"
    }.get(key))

@pytest.fixture
def mock_openai(mocker):
    """Mock OpenAI calls."""
    mock_llm = MagicMock()
    mocker.patch("rag.OpenAI", return_value=mock_llm)
    mock_chat = MagicMock()
    mock_chat.invoke.return_value = "Mocked Chat Response"
    mocker.patch("rag.ChatOpenAI", return_value=mock_chat)
    return mock_llm, mock_chat

@pytest.fixture
def mock_vectorstore(mocker):
    """Mock Pinecone VectorStore."""
    mock_store = MagicMock()
    mocker.patch("rag.PineconeVectorStore.from_existing_index", return_value=mock_store)
    return mock_store

@pytest.fixture
def mock_retriever(mocker):
    """Mock SelfQueryRetriever."""
    mock_retriever = MagicMock()
    mock_retriever.invoke.return_value = [
        MagicMock(page_content="Mocked Document Content 1"),
        MagicMock(page_content="Mocked Document Content 2")
    ]
    mocker.patch("rag.SelfQueryRetriever.from_llm", return_value=mock_retriever)
    return mock_retriever


def test_main_endpoint(mock_env, mock_openai, mock_vectorstore, mock_retriever):
    """Test /response endpoint."""
    # Mock the expected structure of retrieved_docs
    mock_retriever.invoke.return_value = [
        MagicMock(page_content="Mocked Document Content 1"),
        MagicMock(page_content="Mocked Document Content 2")
    ]
    
    # Send request to the endpoint
    response = client.get("/response", params={"user_query": "What are the symptoms of flu?"})
    
    # Assertions
    assert response.status_code == 200
    assert response.json()[0] == "Mocked Chat Response"


def test_process_query(mock_openai, mock_vectorstore, mock_retriever):
    """Test query processing and response generation."""
    # Mock the expected structure of retrieved_docs
    mock_retriever.invoke.return_value = [
        MagicMock(page_content="Mocked Document Content 1"),
        MagicMock(page_content="Mocked Document Content 2")
    ]
    
    query = "What are the causes of diabetes?"
    response, docs = main(query)

    assert response == "Mocked Chat Response"
    assert len(docs) == 2
    assert docs[0].page_content == "Mocked Document Content 1"
    assert docs[1].page_content == "Mocked Document Content 2"


def test_metadata_structure():
    """Validate metadata structure integrity."""
    from rag import metadata_field_info
    assert len(metadata_field_info) == 8
    assert metadata_field_info[0].name == "title"
    assert metadata_field_info[0].type == "string"
