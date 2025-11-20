from typing import Literal, List

class PermissionsUtility:
    def __new__(
        cls,
        permissions:List[
            Literal[
                'admin', 
                'siteadmin', 
                'DesignerEnrollment', 
                'TeacherEnrollment', 
                'teacher', 
                'TaEnrollment'
                'observer', 
                'user', 
                'ObserverEnrollment', 
                'StudentViewEnrollment', 
                'fake_student', 
                'student', 
                'StudentEnrollment', 
                'AccountUser', 
                ':group_member', 
                ':group_leader', 
            ]
        ]
    ):
        instance = set(permissions)
        return instance

class AdminExclusive:
    """
    Permissions set restricting data access to only LMS Admins
    """
    def __new__(cls) -> set:
        instance = PermissionsUtility(permissions=["admin", "siteadmin"])
        return instance
    
class SMEInclusive:
    """
    Permissions set restricting data access to SMEs or those with greater permissions
    """
    def __new__(cls) -> set:
        instance = PermissionsUtility(permissions=["admin", "siteadmin", "TeacherEnrollment", "teacher", "TaEnrollment", "DesignerEnrollment"])
        return instance

class SMEExclusive:
    """
    Permissions set restricting data access to only SMEs
    """
    def __new__(cls) -> set:
        instance = PermissionsUtility(permissions=["TeacherEnrollment", "teacher", "TaEnrollment", "DesignerEnrollment"])
        return instance

class StudentExclusive:
    """
    Permissions set restricting data access to only Students or those with access student view
    """
    def __new__(cls) -> set:
        instance = PermissionsUtility(permissions=["student", "StudentEnrollment", "StudentViewEnrollment", "fake_student"])
        return instance