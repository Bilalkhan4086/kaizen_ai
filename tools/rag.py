from langchain_core.tools import tool
from services.rag import get_rag_chain
from langchain_core.documents import Document

# tool function
@tool
def ask_rag_question(question: str) -> Document:
    """
    Function: ask_rag_question

    Description:
    Retrieves information about the product by querying the internal Retrieval-Augmented Generation (RAG) system. This function is designed to answer user questions regarding product features, functionality, usage, definitions, or concepts based on the indexed product documentation.

    When to Use:
    Call this function whenever a user or another system component requires specific information or an explanation related to the product itself. It acts as the primary interface for accessing documented product knowledge via natural language questions.

    Args:
        question: A string containing the user's question about the product (e.g., "What is the Sandbox?", "How do I create an envelope template?").

    Output:
        A string containing the generated answer, synthesized by the RAG model from the most relevant retrieved documentation passages.
    """
    return get_rag_chain(question)

