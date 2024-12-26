import os
import json
from pinecone import Pinecone 
from openai import OpenAI
from models import RAGInputArticle
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))

def process_rag_input(rag_input_dir):
    article_id = 0

    for filename in os.listdir(rag_input_dir):
        if not filename.endswith('.json'):
            continue
        # file ends with .json
        file_path = os.path.join(rag_input_dir, filename)
        with open(file_path, 'r') as file:
            data = json.load(file)
        article = RAGInputArticle(**data)
        
        vectors = []

        metadata = article.model_dump()
        metadata.pop("chunks")
        metadata["article_id"] = article_id

        for i, chunk in enumerate(article.chunks):
            # Create embedding
            response = client.embeddings.create(
                input=chunk,
                model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding
            metadata["chunk_id"] = i
            metadata["text"] = chunk

            vectors.append(
                {
                    "id": f"{article_id}_{i}",
                    "values": embedding,
                    "metadata": metadata.copy() # copy to avoid mutability issues
                }
            )
        
        index.upsert(vectors=vectors)
        print(f"Upserted {len(vectors)} vectors for article {article_id}")
        article_id += 1

    print("All articles processed and uploaded to Pinecone.")

#FUNCTION TO PRUNE PINECONE DATABASE
def delete_all():
    index.delete(delete_all=True)
    print("All vectors have been deleted from the index.")

if __name__ == "__main__":
    process_rag_input('healthline_complete_rag_input')

# if __name__ == "__main__":
#     delete_all()

    