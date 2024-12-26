import os
from openai import OpenAI
from dotenv import load_dotenv
from models import ResponseStructuredArticle

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an information extraction assistant. Your job is to read health-related articles in markdown format and extract specific fields as structured data. Please follow the guidelines below to ensure the extracted information matches the following schema:

- **title**: The title of the article (string)
- **disease_name**: The name of the disease discussed (string)
- **who_is_at_risk**: A list of people or groups who are most at risk of contracting the disease (list of strings)
- **causes**: A list of known causes or risk factors contributing to the disease (list of strings)
- **symptoms**: A list of symptoms associated with the disease (list of strings)
- **medicines**: A list of medicines commonly used to treat the disease (list of strings)
- **summary**: A brief summary of the article (string)
- **length_of_disease_in_days**: The typical duration of the disease in days (integer)

For list of strings, limit each string to be short (eg. "diabetic" instead of "people with diabetes"). We will perform a SQL-like search on these fields.

You will receive a health-related article in markdown format. Carefully extract the above fields and return the information in the structured format of `ResponseStructuredArticle`.
"""

def openai_parse_markdown(markdown_text: str) -> ResponseStructuredArticle:
    prompt = f"""
    Here is the markdown version of the article that you need to parse:

    ----
    {markdown_text}
    ----
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4o",  
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format=ResponseStructuredArticle
    )

    return response.choices[0].message.parsed


# if __name__ == "__main__":
#     # change to os.walk once tested out
#     for file_path in os.listdir("saved_markdown"):
#         with open(f"saved_markdown/{file_path}", "r", encoding="utf-8") as file:
#             markdown_text = file.read()
#         rag_input_article = openai_parse_markdown(markdown_text).to_chunking_input_article(markdown_text).to_rag_input_article()
#         with open(f"rag_input/{file_path.split('.')[0]}.json", "w") as file:
#             file.write(rag_input_article.model_dump_json(indent=4))


if __name__ == "__main__":
    # change to os.walk once tested out
    for file_path in os.listdir("healthline_markdowns_complete"):
        with open(f"healthline_markdowns_complete/{file_path}", "r", encoding="utf-8") as file:
            markdown_text = file.read()
        rag_input_article = openai_parse_markdown(markdown_text).to_chunking_input_article(markdown_text).to_rag_input_article()
        with open(f"healthline_complete_rag_input/{file_path.split('.')[0]}.json", "w") as file:
            file.write(rag_input_article.model_dump_json(indent=4))
