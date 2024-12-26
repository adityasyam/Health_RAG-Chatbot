from pydantic import BaseModel
from typing import List
from langchain.schema import Document
from typing import Optional
import re
#final structure of article for RAG processing.
class RAGInputArticle(BaseModel):
    title: str
    disease_name: str
    article_id: int
    who_is_at_risk: List[str]
    causes: List[str]
    medicines: List[str]
    summary: str
    symptoms: List[str]
    length_of_disease_in_days: int
    chunks: List[str]
    #converts RAGInputArticle into a list of LangChain Document objects.
    def to_documents(self) -> List[Document]:
        metadata = self.model_dump()
        metadata.pop("chunks")
        return [Document(page_content=chunk, metadata=metadata) for chunk in self.chunks]

#Represents the input article before chunking for RAG processing
class ChunkingInputArticle(BaseModel):
    title: str
    disease_name: str
    article_id: int
    who_is_at_risk: List[str]
    causes: List[str]
    medicines: List[str]
    summary: str
    symptoms: List[str]
    length_of_disease_in_days: int

    cleaned_article_text: str 
    #converts ChunkingInputArticle into a RAGInputArticle.
    def to_rag_input_article(self) -> RAGInputArticle:
        chunks = self.chunk_article()
        return RAGInputArticle(
            title=self.title,
            disease_name=self.disease_name,
            article_id=self.article_id,
            who_is_at_risk=self.who_is_at_risk,
            causes=self.causes,
            medicines=self.medicines,
            summary=self.summary,
            symptoms=self.symptoms,
            length_of_disease_in_days=self.length_of_disease_in_days,
            chunks=chunks
        )
    

    def chunk_article(self, min_chunk_size=100, overlap = 50):
        """
        Takes the article as input (string) and outputs a list of strings (chunks).
        
        Args:
        - min_chunk_size (int): Minimum character length for each chunk.

        Returns:
        - List[str]: List of chunks where each chunk is a string.
        """
        
        pattern = r"(^#{1,3} .+)"  # Matches headers with 1 to 3 `#` symbols (e.g., `#`, `##`, `###`)
        parts = re.split(pattern, self.cleaned_article_text, flags=re.MULTILINE)

        print(len(parts))
        
        chunks = []
        current_chunk = ""

        for part in parts:
            if re.match(r"^#{1,3} .+", part):
                if len(current_chunk.strip()) > min_chunk_size:
                    chunks.append(current_chunk.strip())
                current_chunk = part
            else:
                # add the paragraph/text content to the current chunk
                current_chunk += part
        
        # append the last chunk if it exists and is above the minimum size
        if len(current_chunk.strip()) > min_chunk_size:
            chunks.append(current_chunk.strip())
            
        overlapping_chunks = []
        for i in range(len(chunks)):
            if i == 0:
                overlapping_chunks.append(chunks[i])  # 1st chunk no overlap
            else:
                previous_chunk = chunks[i - 1] # last char of previous chunk
                overlapping_chunks.append(previous_chunk[-overlap:] + " " + chunks[i])
        return overlapping_chunks
        
        #return chunks
#Represents a structured response that can be converted into a ChunkingInputArticle
class ResponseStructuredArticle(BaseModel):
    title: str
    disease_name: str
    article_id: int
    who_is_at_risk: List[str]
    causes: List[str]
    symptoms: List[str]
    medicines: List[str]
    summary: str
    length_of_disease_in_days: int

    def to_chunking_input_article(self, cleaned_article_text: str) -> ChunkingInputArticle:
        return ChunkingInputArticle(
            title=self.title,
            disease_name=self.disease_name,
            article_id=self.article_id,
            who_is_at_risk=self.who_is_at_risk,
            causes=self.causes,
            symptoms=self.symptoms,
            medicines=self.medicines,
            summary=self.summary,
            length_of_disease_in_days=self.length_of_disease_in_days,
            cleaned_article_text=cleaned_article_text
        )

