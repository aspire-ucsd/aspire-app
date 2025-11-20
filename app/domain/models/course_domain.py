from pydantic import BaseModel
from typing import List, Optional, Dict, Union

from app.domain.models.concept_collection import CollectionRead
from app.domain.models.concept import ConceptReadPreformatted, ConceptToConceptRead

class CourseDomain(BaseModel): 
    collections: Optional[Union[List[CollectionRead], list]] = []
    concepts: Optional[Union[Dict[str, ConceptReadPreformatted], dict]] = {}
    junctions: Optional[Union[List[ConceptToConceptRead], list]] = []
