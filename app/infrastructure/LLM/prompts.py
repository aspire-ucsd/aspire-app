base_prompt = """
You are a subject matter expert in the subject of {subject},
tutoring students with {difficulty} skill level. The name of the
course you teach is {name}. This is a domain map of the course
content: {content_summary}. You must provide accurate responses
based upon the context provided to you in json.
"""

def generateRolePrompt():
        """
            Generates the base prompt on class instantiation, contains the role and context sections of the final prompt.
        """
        #TODO: replace with db query to domain table using self.domain_id
        domain_data = {
            "name": "css1", 
            "subject": "computer science", 
            "difficulty": "introductory", 
            "content_summary": "introductory python course"
            }
        role_prompt = role_prompt = base_prompt.format(**domain_data)

        return role_prompt