from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os
import re
from rag import main
from disease_names import json_files

load_dotenv()

# Initialize vector store and conversation components
vectorstore = PineconeVectorStore.from_existing_index(
    index_name=os.getenv("PINECONE_INDEX_NAME"),
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
)

memory = ConversationBufferMemory()
llm = ChatOpenAI(model="gpt-4", temperature=0)
conversation_chain = ConversationChain(llm=llm, memory=memory)

# Global state tracking
current_patient_context = None
conversation_state = {
    "questions_asked": 0,
    "enough_context": False,
    "relevance_scores": [],
    "feedback": [],
}

# Updates the conversation context with patient-specific details and integrates it into memory.
def update_conversation_context(patient_data: dict, test=False):
    global current_patient_context
    current_patient_context = patient_data
    
    # Update conversation memory with patient context
    context_message = f"Patient #{patient_data['patient_number']} Context:\n" \
                     f"Past Medical History: {', '.join(patient_data['past_history'])}\n" \
                     f"Family History: {', '.join(patient_data['family_history'])}"
    
    memory.save_context(
        {"input": "System: Updating patient context"}, 
        {"output": context_message}
    )

    if test:
        return current_patient_context

# Detect diseases mentioned in the given text using word boundaries
# to ensure only complete matches are detected.
def detect_diseases_in_text(text):
    known_diseases = json_files
    detected_diseases = []
    for disease in known_diseases:
        if re.search(rf'\b{re.escape(disease)}\b', text, re.IGNORECASE):
            detected_diseases.append(disease)
    return detected_diseases

# Fetches follow-up questions based on the user's input using our RAG model
def query_follow_up_questions(user_input):

    response, retrieved_docs = main(user_input)
    questions = []

    for doc in retrieved_docs:
        related_questions = doc.metadata.get("follow_up_questions", [])
        questions.extend(related_questions)

    return questions

# Generates responses considering patient context and conversation_state
def generate_chat_response(user_query: str) -> str:
    try:
        # Enhance query with patient context if available
        if current_patient_context and not user_query.startswith("Based on the patient #"):
            user_query = f"Considering patient #{current_patient_context['patient_number']}'s " \
                        f"medical history, answer the following: {user_query}"
        
        chat_response = conversation_chain.predict(input=user_query)
        
        # Update conversation state
        conversation_state["questions_asked"] += 1
        
        # Add follow-up questions
        follow_up_questions = query_follow_up_questions(user_query)
        if follow_up_questions:
            chat_response += "\n\nFollow-up Questions:\n" + "\n".join(f"- {q}" for q in follow_up_questions)

        # Check if we have enough context for document retrieval
        if conversation_state["questions_asked"] > 4 and not conversation_state["enough_context"]:
            conversation_state["enough_context"] = True
            chat_response += "\n\nI believe I now have enough information. Let me check for relevant documents..."
            
            response, retrieved_docs = main(user_query)
            if retrieved_docs:
                suggested_docs = []
                for doc in retrieved_docs[:3]:
                    title = doc.metadata.get("title", "No Title")
                    score = doc.metadata.get("score", "No Score Provided")
                    suggested_docs.append(f"Document: {title} (Relevance: {score})")
                chat_response += "\n\nRelevant Documents:\n" + "\n".join(suggested_docs)
                conversation_state["relevance_scores"] = [doc.metadata.get("score", 0) for doc in retrieved_docs[:3]]

        # Add disease sources
        detected_diseases = detect_diseases_in_text(chat_response)
        if detected_diseases:
            sources = ", ".join([f"article on {disease} from healthline.com" for disease in detected_diseases])
            chat_response += f"\n\nSources: {sources}"

        # Reset context after document retrieval
        if conversation_state["enough_context"]:
            conversation_state["questions_asked"] = 0
            conversation_state["enough_context"] = False

        return chat_response

    except Exception as e:
        print(f"Error generating response: {e}")
        return "I apologize, but I encountered an error processing your request."

# Feature to be developed further: Collecting user feedback on retrieved
#                                   documents to improve model
def gather_feedback(retrieved_docs):
    feedback_entries = []
    for i, doc in enumerate(retrieved_docs, start=1):
        feedback = input(f"\nWas Document {i} ('{doc.metadata.get('title', 'No Title')}') helpful? (yes/no): ").strip().lower()
        feedback_entries.append({"doc": doc.metadata.get("title"), "feedback": feedback})

    conversation_state["feedback"].extend(feedback_entries)

if __name__ == "__main__":
    print("Welcome to the Conversational AI Health Bot with real-time suggestions. Type 'exit' to quit.")
    print("I'll tailor my questions based on your input and patient context when available.\n")

    while True:
        user_query = input("\nYou: ")
        if user_query.lower() == "exit":
            print("Goodbye :)")
            break

        try:
            response = generate_chat_response(user_query)
            print(f"AI: {response}")

            # Gather feedback if documents were returned
            if conversation_state["relevance_scores"]:
                response, retrieved_docs = main(user_query)
                gather_feedback(retrieved_docs)
                print("Thanks for the feedback!")
        except Exception as e:
            print(f"Error: {e}")