from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAI, ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os
import re
from rag import main
from disease_names import json_files

load_dotenv()

# starting Pinecone vector store
vectorstore = PineconeVectorStore.from_existing_index(
    index_name=os.getenv("PINECONE_INDEX_NAME"),
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
)
# Conversational memory to maintain context
memory = ConversationBufferMemory()
llm = ChatOpenAI(model="gpt-4o", temperature=0)
conversation_chain = ConversationChain(llm=llm, memory=memory)
# tracking state to see if ready to return documents and feedback (still have to implement!)
conversation_state = {
    "questions_asked": 0,
    "enough_context": False,
    "relevance_scores": [],
    "feedback": [],
}

def detect_diseases_in_text(text):
    """
    Detect diseases mentioned in the given text using word boundaries
    to ensure only complete matches are detected.
    """
    # A list of common diseases for detection
    known_diseases = json_files

    detected_diseases = []
    for disease in known_diseases:
        # Use word boundaries to match whole words only
        if re.search(rf'\b{re.escape(disease)}\b', text, re.IGNORECASE):
            detected_diseases.append(disease)
    return detected_diseases


def query_follow_up_questions(user_input):
    """
    Fetches follow-up questions based on the user's input using our RAG model
    """
    response, retrieved_docs = main(user_input)
    questions = []
    for doc in retrieved_docs:
        # assuming that follow-up questions are stored in metadata as a list
        related_questions = doc.metadata.get("follow_up_questions", [])
        questions.extend(related_questions)
    return questions
def generate_chat_response(user_query):
    """
    Handles the chat's response logic, including real-time questions and retrieval
    of documents.
    """
    chat_response = conversation_chain.predict(input=user_query)
    # Increment questions asked and see if we have enough context
    conversation_state["questions_asked"] += 1
    follow_up_questions = query_follow_up_questions(user_query)
    if follow_up_questions:
        chat_response += "\n\nFollow-up Questions:\n" + "\n".join(f"- {q}" for q in follow_up_questions)

    # End with document retrieval after enough questions
    if conversation_state["questions_asked"] > 4 and not conversation_state["enough_context"]:
        conversation_state["enough_context"] = True
        chat_response += (
            "\n\nI believe I now have enough information. Let me check for relevant documents..."
        )
        # Query Pinecone for relevant documents
        response, retrieved_docs = main(user_query)
        if retrieved_docs:
            suggested_docs = []
            for doc in retrieved_docs[:3]:
                title = doc.metadata.get("title", "No Title")
                score = doc.metadata.get("score", "No Score Provided")
                suggested_docs.append(f"Document: {title} (Relevance: {score})")
            chat_response += "\n\nRelevant Documents:\n" + "\n".join(suggested_docs)
            conversation_state["relevance_scores"] = [doc.metadata.get("score", 0) for doc in retrieved_docs[:3]]

    # Append source information for detected diseases
    detected_diseases = detect_diseases_in_text(chat_response)
    if detected_diseases:
        sources = ", ".join([f"article on {disease} from healthline.com" for disease in detected_diseases])
        chat_response += f"\n\nSources: {sources}"

    # Resetting the context after returning documents
    if conversation_state["enough_context"]:
        conversation_state["questions_asked"] = 0
        conversation_state["enough_context"] = False
    return chat_response
def gather_feedback(retrieved_docs):
    """
    Collect user feedback for each document returned.
    """
    feedback_entries = []
    for i, doc in enumerate(retrieved_docs, start=1):
        feedback = input(f"\nWas Document {i} ('{doc.metadata.get('title', 'No Title')}') helpful? (yes/no): ").strip().lower()
        feedback_entries.append({"doc": doc.metadata.get("title"), "feedback": feedback})
    conversation_state["feedback"].extend(feedback_entries)
# Main loop for terminal chatting
if __name__ == "__main__":
    print("Welcome to the Conversational AI Health Bot with real-time suggestions. Type 'exit' to quit.")
    print("I'll tailor my questions based on your input. I'll let you know if I need more information or when I find relevant documents.\n")
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() == "exit":
            print("Goodbye :)")
            break
        try:
            response = generate_chat_response(user_query)
            print(f"AI: {response}")
            # Gather user feedback after documents are returned
            if conversation_state["relevance_scores"]:
                response, retrieved_docs = main(user_query)
                gather_feedback(retrieved_docs)
                print("Thanks for the feedback!")
        except Exception as e:
            print(f"Error: {e}")