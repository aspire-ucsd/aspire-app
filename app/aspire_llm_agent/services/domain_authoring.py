from typing import List, Coroutine, Optional

from ..chains.concept_id import concept_id_chain

from ..utils import split_docs, get_files_from_url
from langchain_core.globals import set_debug, set_verbose

async def identify_concepts_in_batches(
        source_locations: List[str],
        course_subjects: str,
        course_summary: str,
        storage_method: Coroutine,
        document_loader: Coroutine = get_files_from_url,
        document_splitter: Coroutine = split_docs,
        document_enricher: Optional[Coroutine] = None,
        extra_params: dict = {}
    ):
    """
    Iteratively retrieves documents at each source location, 
    splits each into smaller chunks, optionally enriches each chunk with additional context, 
    then processes the whole group in parallel identifying all concepts contained within and stores those concepts between iterations. 

    :param source_locations: List of valid URLS pointing to course materials. 
    :param course_subjects: String containing all subjects the course belongs to.
    :param course_summary: String containing a summary of the course.
    :param storage_method: Async function called at the end of each document processing iteration to store the intermediate results. Must accept 'results' and 'extra_params' as kwargs.
    :param document_loader: Async function called at the start of each iteration to retrieve the documents from their source location. Must accept 'location' and 'extra_params' as kwargs.
    :param document_splitter: Async function called after documents have been retrieved, splits the documents into manageable chunks for the LLM. Must accept 'document' and 'extra_params' as kwargs.
    :param document_enricher: Optional async function called after documents have been split, used to enrich documents with extra data prior to processing by the LLM. Must accept 'docs' and 'extra_params' as kwargs.
    :param extra_params: Passed into the document_loader, document_splitter, document_enricher, concept_id_agent, and storage_method to dictate various behaviors.

    ======================
    storage_method example:
    ======================
    This function determines how and where intermediate results are stored, without it the results would just be tossed out.

    ```python
    async def storage_method(results:str, extra_params:dict={}):
        with open(extra_params.get("storage_location"), "w") as file:
            json.dump(results, file)
    ```

    ======================
    document_loader example:
    ======================
    This function determines how files are retrieved from various URLs and is in charge of handling various retrieval methods dependent on the source. 
    The expected return would be in the form of LangChain Document Objects.
    ```python
    async def document_retriever(location:str, extra_params:dict={}):
        response = requests.get(location)
        response.raise_for_status()
        return response.content
    ```
    """
    set_debug(True)
    set_verbose(True)
    for location in source_locations:
        document = await document_loader(location=location, extra_params=extra_params)
        if document:
            split_docs = await document_splitter(document=document, extra_params=extra_params)

        if document_enricher and split_docs:
            split_docs = await document_enricher(docs=split_docs, extra_params=extra_params)
        #TODO: Remove document quantity limitation added for tests
        results = await concept_id_chain(
            documents=split_docs, 
            subjects=course_subjects, 
            course_summary=course_summary,
            is_enriched=bool(document_enricher),
            extra_params=extra_params
            )

        await storage_method(results=results, extra_params=extra_params)
