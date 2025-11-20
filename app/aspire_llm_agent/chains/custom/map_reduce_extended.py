from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from typing import Any, List, Optional, Tuple
from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document

class MRDExtended(MapReduceDocumentsChain):
    """
    Extends MapReduceDocumentsChain to allow additional Document variables to be added to the mapping prompt. 
    When used with extentions of the Document class, allows for individualized document enrichment. 

    :param additional_doc_vars: Extra keys to append to the input variables list for prompt variable injection. 
    """
    additional_doc_vars: Optional[List[str]] = []

    async def acombine_docs(
        self,
        docs: List[Document],
        token_max: Optional[int] = None,
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> Tuple[str, dict]:
        """Combine documents in a map reduce manner.

        Combine by mapping first chain over all documents, then reducing the results.
        This reducing can be done recursively if needed (if there are many documents).
        """
        map_results = await self.llm_chain.aapply(
            # FYI - this is parallelized and so it is fast.
            [{**{self.document_variable_name: d.page_content}, **{key: d.model_dump().get(key) for key in self.additional_doc_vars}, **kwargs} for d in docs],
            callbacks=callbacks,
        )
        question_result_key = self.llm_chain.output_key
        result_docs = [
            Document(page_content=r[question_result_key], metadata=docs[i].metadata)
            # This uses metadata from the docs, and the textual results from `results`
            for i, r in enumerate(map_results)
        ]
        
        result, extra_return_dict = await self.reduce_documents_chain.acombine_docs(
            result_docs, token_max=token_max, callbacks=callbacks, **kwargs
        )
        if self.return_intermediate_steps:
            intermediate_steps = [r[question_result_key] for r in map_results]
            extra_return_dict["intermediate_steps"] = intermediate_steps
        return result, extra_return_dict