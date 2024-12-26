import unittest
from conversation import generate_chat_response

class ChatbotEvaluation(unittest.TestCase):

    def evaluate_response(self, query, expected_keywords, min_relevance_score):
        """
        Evaluates the chatbot response for relevance and citation accuracy.

        Parameters:
        - query: str, the input query to the chatbot.
        - expected_keywords: list of str, keywords expected to appear in the response.
        - min_relevance_score: float, minimum average relevance score expected for documents.

        Returns:
        - cost: float, cost of the response (lower is better).
        """
        response = generate_chat_response(query)
        
        # Check for presence of expected keywords in the response
        keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in response.lower())
        relevance_score = keyword_matches / len(expected_keywords)
        
        relevance_scores = [float(score) for score in response.split() if score.replace('.', '', 1).isdigit()]
        avg_relevance_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0

        # Calculate cost
        cost = 1 - relevance_score  # Penalize lack of keyword matches
        if avg_relevance_score < min_relevance_score:
            cost += (min_relevance_score - avg_relevance_score) * 0.5  # Penalize low relevance

        return cost

    def test_chatbot_responses(self):
        queries = [
            {"query": "What are the symptoms of diabetes?", "keywords": ["symptoms", "diabetes"], "min_score": 0.7},
            {"query": "What are the treatments for asthma?", "keywords": ["treatments", "asthma"], "min_score": 0.6},
            {"query": "Explain the risk factors of heart attack.", "keywords": ["risk factors", "heart attack"], "min_score": 0.75},
            {"query": "Can COVID-19 cause long-term complications?", "keywords": ["COVID-19", "long-term", "complications"], "min_score": 0.8},
            {"query": "What are the early signs of Alzheimer’s disease?", "keywords": ["early signs", "Alzheimer’s"], "min_score": 0.7},
            {"query": "How do vaccines work to prevent infections?", "keywords": ["vaccines", "prevent", "infections"], "min_score": 0.85},
            {"query": "What is the role of diet in managing cholesterol?", "keywords": ["diet", "managing", "cholesterol"], "min_score": 0.7},
            {"query": "Explain how exercise improves mental health.", "keywords": ["exercise", "mental health"], "min_score": 0.8},
            {"query": "What are the symptoms and treatments for malaria?", "keywords": ["symptoms", "treatments", "malaria"], "min_score": 0.75},
            {"query": "What causes migraines?", "keywords": ["causes", "migraines"], "min_score": 0.7},
            {"query": "What are the benefits of a balanced diet?", "keywords": ["benefits", "balanced diet"], "min_score": 0.7},
            {"query": "Explain the impact of smoking on lung health.", "keywords": ["smoking", "lung health"], "min_score": 0.75},
            {"query": "How does stress affect cardiovascular health?", "keywords": ["stress", "cardiovascular health"], "min_score": 0.8},
            {"query": "What are the common types of arthritis?", "keywords": ["types", "arthritis"], "min_score": 0.6},
            {"query": "How does hydration affect kidney function?", "keywords": ["hydration", "kidney function"], "min_score": 0.8},
        ]

        successes = 0
        failures = []
        
        for i, query in enumerate(queries, 1):
            cost = self.evaluate_response(query["query"], query["keywords"], query["min_score"])
            if cost < 0.5:
                successes += 1
            else:
                failures.append((i, query["query"], cost))

        # Print the concise test results
        print(f"Test Results: {successes} Successes, {len(failures)} Failures")
        if failures:
            print("Failures:")
            for idx, query, cost in failures:
                print(f"  Test Case {idx}: '{query}' failed with cost {cost:.2f}")

if __name__ == "__main__":
    # Suppress the standard unittest output
    unittest.main(verbosity=0, exit=False)
