# Normal Testing first, not self-querying retrieval testing

import os
from pinecone import Pinecone
from dotenv import load_dotenv
from models import RAGInputArticle
from langchain_openai import OpenAI, OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.retrievers.self_query.base import SelfQueryRetriever
from rag import metadata_field_info, document_content_description

load_dotenv()

# Initializes Pinecone w/ API credentials and ensure the index exists
def init_pinecone():
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")

    pc = Pinecone(api_key=api_key)

    if index_name not in pc.list_indexes().names():
        raise ValueError(f"Index '{index_name}' not found.")

    return pc.Index(index_name)

# Create a embedding vector for a given prompt using OpenAI's embedding model
def create_embedding(prompt: str):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_api_key)
    
    response = client.embeddings.create(input=prompt, model="text-embedding-ada-002")
    return response.data[0].embedding

# Retrieve top-k matching articles from Pinecone based on the input query
def retrieve_article_from_pinecone(query: str, index):
    embedding = create_embedding(query)
    result = index.query(vector=embedding, top_k=3, include_metadata=True)

    article_ids = [match['id'] for match in result['matches']]
    for match in result['matches']:
        print(f"Article ID: {match['id']}, Score: {match['score']}")
    
    return article_ids

def test_article_retrieval(index):
    test_cases = [
        ("I have conjunctivitis or a red eye", ["6_5", "19_21", "22_29"]),
        ("I have abdominal pain", ["5_11", "5_13", "13_13"]),
        ("I feel dizzy and have a headache", ["5_11", "5_13", "5_7"])
    ]

    for query, expected_ids in test_cases:
        print(f"\nTesting Query: '{query}'")
        article_ids = retrieve_article_from_pinecone(query, index)
        for expected_id in expected_ids:
            if expected_id in article_ids:
                print(f"Success: Expected ID '{expected_id}' found.")
                break

def main():
    index = init_pinecone() 
    test_article_retrieval(index)  # run tests

# Initialize retriever with LangChain's SelfQueryRetriever and metadata configuration
def get_retriever():
    from dotenv import load_dotenv
    import os
    load_dotenv()


    llm = OpenAI(temperature=0)
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        embedding=OpenAIEmbeddings(model="text-embedding-3-small")
    )
    retriever = SelfQueryRetriever.from_llm(
        llm, vectorstore, document_content_description, metadata_field_info, verbose=True
    )
    
    return retriever

# def test_retrieval(retriever : SelfQueryRetriever, query, article_id):
#     docs = retriever.invoke(query)
#     assert article_id in [doc.metadata["article_id"] for doc in docs]

# Test a query's retrieval against an expected article ID, logging successes and failures
def test_retrieval(retriever: SelfQueryRetriever, query: str, article_id: int, passed_tests: list, failed_tests: list):
    try:
        docs = retriever.invoke(query)
        retrieved_article_ids = [doc.metadata["article_id"] for doc in docs]  # Gets the retrieved article IDs

        if article_id in retrieved_article_ids:
            print(f"Test Passed for Query: '{query}'")
            passed_tests.append(query)
        else:
            print(f"Test Failed for Query: '{query}'")
            print(f"    Expected Article ID: {article_id}")
            print(f"    Retrieved Article IDs: {retrieved_article_ids}")  # Shows what was actually retrieved by model
            failed_tests.append(query)
    except Exception as e:
        print(f"Test Failed for Query: '{query}' - Error: {e}")
        failed_tests.append(query)
    

# Run self-query retrieval tests and output test results over here
if __name__ == "__main__":
    passed_tests = []
    failed_tests = []
    retriever = get_retriever()

    test_cases = [
        ("What is psychotherapy useful for?", 0),
        ("I am a man over 45 years of age and have cholesterol plaque buildup", 16),
        ("What are the symptoms of fungal skin infections", 25),
        ("I have nausea and vomiting", 26),
        ("Tell me about colitis", 31),
        ("What can I use methadone and suboxone for?", 49),
        ("My brother is experiencing cramping and crazy abdominal pain", 51),
        ("I have hormonal imbalance and am currently experiencing painful intercourse", 67),
        ("Can I use antiepileptic drugs for seizures?", 78),
        ("Can I use antifungal ointment to cure blisters", 84),
        ("What is the common name for Addison's disease?", 96),
        ("I have a stiff neck. Is this coz of my poor posture at work?", 105),
        ("Tell me about gout", 119),
        ("What can minoxidil help with?", 121),
        ("What happens when your digestive system cannot tolerate certain foods", 134),
        ("My grandpa has osteoporosis and has difficulty walking", 140),
        ("I have loose and watery stools", 151),
        ("My toddler has been making a barking cough sound and seems to have trouble breathing. What could this be?", 20),
        ("I've been dealing with stomach pain and frequent diarrhea. Could this have something to do with inflammation in my gut?", 31),
        ("Lately, my knees and other joints feel really stiff in the mornings. Is this normal as you age?", 29),
        ("After eating at a food truck last night, I woke up with severe stomach cramps and nausea. What could cause this?", 35),
        ("I've had some numbness in my legs and trouble with coordination recently. Could this be something serious?", 33),
        ("Every time I eat a big meal and lie down, I feel a burning sensation in my chest. Is this related to digestion?", 111),
        ("Can you explain the ways someone might contract a virus through bodily fluids?", 37),
        ("I've noticed my periods have been irregular and painful recently. Should I be concerned?", 38),
        ("I've been diagnosed with Parkinson's. Are there exercises or diets that could help me manage my symptoms better?", 44),
        ("I've been having back pain that gets worse when I sit for too long. Any idea why?", 77),
        ("I've been smoking for many years. Are there any early signs of lung issues I should watch out for?", 110),
        ("I've been having chest pain and feeling out of breath. Could it be heart-related?", 131),
        ("My kid wakes up screaming at night but doesn't remember anything the next day.", 47),
        ("I found some painful sores in a sensitive area. It's been bothering my skins.", 83),
        ("My hip has been hurting when I walk or climb stairs recently.", 140),
        ("I'm having trouble hearing in one ear, and there's a constant ringing sound.", 148)
    ]


    for query, article_id in test_cases:
        test_retrieval(retriever, query, article_id, passed_tests, failed_tests)

    total_tests = len(test_cases)
    passed_count = len(passed_tests)
    failed_count = len(failed_tests)
    passed_percentage = (passed_count / total_tests) * 100

    print("\nTest Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_count}")
    print(f"Failed Tests: {failed_count}")
    print(f"Percentage Passed: {passed_percentage:.2f}%")
    
    