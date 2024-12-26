## Self-querying retriever using RAG and conversational AI for healthcare applications

This project aims to use self-querying retrieval and structured outputs to create a better RAG process targeted towards medical applications specifically. This will allow patients to find similar cases to theirs, and allow doctors to more easily diagnose patients with little to no additional effort. 

## Usage
Set up a venv with a python version >= `python3.12`. Create a virtual environment using command `python3.12 -m venv .venv`. Activate the virtual environment (activation instructions vary by OS. Install the required python packages by running `pip install -r backend/requirements.txt`. 

All subsequent launch steps are contained in the bash script `launch-all.sh`. Give it execution permissions by running `chmod +x launch-all.sh`. Then, load the frontend by calling the script: `./launch-all.sh`. The frontend can be accessed through `http://localhost:3000` now. The backend can be tested manually by navigating to `http://localhost:8000/docs`. 

A sample .txt file to be used for testing the patient upload record feature can be found in archive (named `sample_patient_record.txt`). A PDF version for testing the patient record feature can also be found (named `Patient Record.pdf`).

The audio feature can simply be used by recording audio (give permission to record if needed) and waiting for the audio response.

## Environment variables
To replicate this directory, you would want to create your own private variables for OpenAI and Pinecone. You could upsert the structured JSON RAG inputs into Pinecone (from `healthline_complete_rag_input`) or create your own structured data for the RAG input. Either way, you would create a new Pinecone vector database with data of your choice and then use the OpenAI private keys to run the other parts of the program.

A full list of environment variables needed is:
1) PINECONE_API_KEY
2) PINECONE_INDEX_NAME
3) PINECONE_ENV
4) OPENAI_API_KEY
5) ASSEMBLYAI_API_KEY

### Testing

There are multiple test suites within the codebase.

The RAG testing (ML-style testing) can be run by running `python3 backend/RAG_Testing.py`.

The Pytest unit tests (modular style SWE testing) can be run by running
`pytest backend/test_detect_diseases_in_text.py`
`pytest backend/test_generate_chat_response.py`
`pytest backend/test_query_follow_up.py`
`pytest backend/test_rag.py`
`pytest backend/test_system_state.py`
`pytest backend/test_update_conversation.py`

The final cost function test can be run by running `python backend/accuracy_test.py`