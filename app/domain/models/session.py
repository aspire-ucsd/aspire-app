from fastapi_lti1p3 import Session
from typing import Optional, List, Dict, Union
from app.domain.models.client import ClientRead

class SessionExtended(Session):
    course_metadata: Optional[dict] = {}
    params: Optional[dict] = {}
    concepts_to_be_tested: Optional[List] = []
    question_ids: Optional[List] = []
    knowledge_state: Optional[Dict] = {}


    def get_roles(self):
        return self.user_credentials.user_vars['roles']
    
    def set_roles(self):
        user_credentials = self.user_credentials
        user_credentials.user_vars["roles"] = set(self.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("roles").split(","))

        try:
            setattr(self, 'user_credentials', user_credentials)

        except ValueError:
            pass

    def set_platform_id(self) -> Union[int, str, None]:
        id = self.id_token.get("https://purl.imsglobal.org/spec/lti/claim/custom").get("user_id")
        user_credentials = self.user_credentials
        user_credentials.platform_id = id

        try:
            setattr(self, 'user_credentials', user_credentials)

        except ValueError:
            pass
