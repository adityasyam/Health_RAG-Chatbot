from langchain_openai import OpenAI, OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from voice import text_to_speech, speech_to_text


app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define metadata fields for articles retrieved from the vector store
metadata_field_info = [
    AttributeInfo(
        name="title",
        description="The title of the article",
        type="string",
    ),
    AttributeInfo(
        name="disease_name",
        description="The name of the disease discussed in the article",
        type="string",
    ),
    AttributeInfo(
        name="who_is_at_risk",
        description="List of groups or people who are at risk of the disease. For example: 'pregnant', 'diabetic', 'old', etc.",
        type="list of strings",
    ),
    AttributeInfo(
        name="causes",
        description="List of causes or factors contributing to the disease. For example: 'smoking', 'obesity', 'pollution', etc.",
        type="list of strings",
    ),
    AttributeInfo(
        name="medicines",
        description="List of medicines used to treat the disease. For example: 'aspirin', 'insulin', 'penicillin', etc.",
        type="list of strings",
    ),
    AttributeInfo(
        name="symptoms", 
        description="List of symptoms associated with the disease. For example: 'cough', 'fever', 'headache', etc.",
        type="list of strings",
    ),
    AttributeInfo(
        name="length_of_disease_in_days",
        description="The typical length or duration of the disease in days.",
        type="integer",
    ),
    AttributeInfo(
        name="summary",
        description="A brief summary of the article",
        type="string",
    ),
]

# Description of the document content stored in Pinecone
document_content_description = "Brief summary of the healthcare article discussing diseases, treatments, symptoms, and at-risk individuals"

@app.get("/response")
def main(user_query : str):
    # Handles user queries by retrieving relevant documents and generating AI responses.
    from dotenv import load_dotenv
    import os
    load_dotenv()


    llm = OpenAI(temperature=0)
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding=OpenAIEmbeddings(model="text-embedding-ada-002")
    )
    retriever = SelfQueryRetriever.from_llm(
        llm, vectorstore, document_content_description, metadata_field_info, verbose=True
    )

    # create a ChatOpenAI instance for generating responses
    chat_model = ChatOpenAI(model="gpt-4o", temperature=0)

    # function to generate a response based on retrieved documents
    def generate_response(query, retrieved_docs):
        # combine the content of retrieved documents
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # construct the prompt for the chat model
        prompt = f"""Based on the following information, please answer the user's question. Use as much context as possible, and try to reduce your use of your own knowledge (the context knowledge is a lot more updated than you).

        Context:
        {context}

        User's question: {query}

        Answer:"""

        response = chat_model.invoke(prompt)
        return response

    def process_query(query):
        retrieved_docs = retriever.invoke(query)
        
        response = generate_response(query, retrieved_docs)
        
        return response, retrieved_docs

    query = user_query
    response, retrieved_docs = process_query(query)
    
    return response, retrieved_docs

# Handles voice input by converting speech to text, processing the query, and 
# generating a voice response.
@app.post("/voice")
async def get_voice_response(audio_file: UploadFile):
    # Convert audio stream to text
    user_query = await speech_to_text(audio_file)
    
    # Get response using main function
    response, _ = main(user_query)
    
    # Convert response to audio
    audio_response = await text_to_speech(response.content)
    return audio_response

if __name__ == "__main__":
    main(input("What would you like to know?"))
