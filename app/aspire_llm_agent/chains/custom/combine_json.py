import json

from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document

from langchain.chains.combine_documents.base import BaseCombineDocumentsChain

from typing import List, Optional, Any, Tuple

class CombineJSONDocsChain(BaseCombineDocumentsChain):
    async def acombine_docs(
        self,
        docs: List[Document],
        token_max: Optional[int] = None,
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> Tuple[str, dict]:
        unique_result = {}
        
        for document in docs:
            try:
                concepts = json.loads(document.page_content)

                for item in concepts:
                    name = item.get(self.name, "").lower()
    
                    if name and name not in unique_result:
                        unique_result[name] = item

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for document: {e}")
                continue

        result = json.dumps(list(unique_result.values())).lower()
        return result, {}
    
    def combine_docs(
        self,
        docs: List[Document],
        token_max: Optional[int] = None,
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> Tuple[str, dict]:
        unique_result = {}
        
        for document in docs:
            try:
                concepts = json.loads(document.page_content)

                for item in concepts:
                    name = item.get("name", "").lower()
    
                    if name and name not in unique_result:
                        unique_result[name] = item

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for document: {e}")
                continue

        result = json.dumps(list(unique_result.values()))
        return result, {}