from langchain_core.documents import Document
from typing import List, Coroutine, Any

class DocumentExtended(Document):
    context_concepts: str

    def __init__(self, context_concepts: str, **kwargs: Any) -> None:
        """Pass context_concepts in as positional or named arg."""
        super().__init__(context_concepts=context_concepts, **kwargs)

async def concept_document_enricher(docs:List[Document], extra_params:dict={}):
    concept_retreiver_func = extra_params.get("concept_retreiver_func")

    if not concept_retreiver_func or isinstance(concept_retreiver_func, Coroutine):
        raise ValueError("'extra_params' arg passed to 'concept_document_enricher' requires dict key 'concept_retreiver_func' with value of type 'Coroutine'")
    
    concept_list = await concept_retreiver_func(params=extra_params)
    new_docs = []
    concept_list = [item.model_dump() for item in concept_list]
    for doc in docs:
        new_doc = DocumentExtended(page_content=doc.page_content, metadata=doc.metadata, context_concepts=str(concept_list[:10]))
        new_docs.append(new_doc)

    return new_docs