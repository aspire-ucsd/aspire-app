import logging
import json

from app.app.errors.llm_response_error import LLMResponseError
from app.domain.models.question import QuestionCreate, AnswerPreCreate

logger = logging.getLogger(__name__)

async def format_questions(response, validator_status, params):
    try:
        questions = []
        for index, question in enumerate(response['questions']):
            question_obj = QuestionCreate(
                    **question, 
                    position=index+1, 
                    question_type="multiple_choice_question",
                    points_possible=5
                    )
            answer_obj = [AnswerPreCreate(**answer) for answer in question["answers"]]
            questions.append({"question": question_obj, "answers": answer_obj})

        return questions
    
    except Exception as e:
        logger.exception(msg="Failed to parse LLM response")
        raise LLMResponseError(
            message="Failed to parse LLM response.", 
            action="questions",
            status_code=500, 
            failed_validators=[str(validator) for validator in validator_status if validator.status == 'FAIL'], 
            llm_response=response
            )


async def check_answer(response, index, item):
    # Expected structure for answers
    expected_answers = {
        "answer_text": str,
        "answer_weight": int,
        "answer_feedback": str
    }

    answer_list = item.get("answers")

    # If there are no answers or the answers are not a list, remove the question
    if not answer_list or not isinstance(answer_list, list):
        response["questions"].pop(index)
        return

    # Loop through each answer and check its structure
    for a_index, answer in enumerate(answer_list):
        if all(expected_answers[key] == type(answer.get(key)) for key in expected_answers):
            continue
        else:
            # Attempt to fix answers with missing or incorrect fields
            new_answer = {}
            for key in expected_answers:
                value = answer.get(key)
                if isinstance(value, expected_answers[key]):
                    new_answer[key] = value
                else:
                    # Provide a placeholder or default value if the type is incorrect or missing
                    if key == "answer_text":
                        new_answer[key] = value if isinstance(value, str) else "Missing answer text"
                    elif key == "answer_weight":
                        new_answer[key] = value if isinstance(value, int) else 0
                    elif key == "answer_feedback":
                        new_answer[key] = value if isinstance(value, str) else "No feedback provided"

            response["questions"][index]["answers"][a_index] = new_answer

    return "PASS", response



async def check_contents_question_list(self, response, validator_status, prompt, action, params):
    """
    ---
    Validation Function 
    ---

    Checks each item of a list of objects assigned to the key: 'questions', validates that each item is a dictionary with the correct keys and values.
    
    ---
    Failure Conditions
    ---

    | Cause of Failure | Failure Mode | Outcome |
    | :--------------- | :----------: | :------ |
    | Response is not a dictionary with the key 'questions' | Safe | No Effect |
    | Value at key 'questions' is not a list | Safe | No Effect |
    | List is empty | Deadly | LLMResponseError |
    | List value not a dictionary | Safe | Checks if value is unprocessed JSON, processes if it is, otherwise it is removed |
    | Object is missing a required key | Safe | Adds the key and value either with an alternative value from the object not already assigned to a correct key or with a placeholder |
    """
    
    if not isinstance(response, dict) or 'questions' not in response:
        self.error_response = "Response is not a dictionary with the key 'questions'"
    print("check_contents_question_list: FAIL - No 'questions' key")
    return "FAIL", response
    
    if not isinstance(response["questions"], list):
        self.error_response = f"Response value at key 'questions' is not a list. Received: {type(response['questions'])}"
        print(f"check_contents_question_list: FAIL - 'questions' not a list")
        return "FAIL", response
    
    if not response['questions']:
        self.error_response = "Questions list is empty"
        print("check_contents_question_list: FAIL - Questions list is empty")
        raise LLMResponseError(
            message="Response contains no values", 
            action="questions", 
            status_code=500, 
            llm_response=response, 
            failed_validators=[str(validator) for validator in validator_status if validator.status == 'FAIL']
        )

    expected_keys = {
        "question_name": str, 
        "question_text": str, 
        "neutral_comments": str, 
        "answers": list
    }

    for index, item in enumerate(response['questions']):
        if not isinstance(item, dict):
            try:
                item = json.loads(item)
                response['questions'][index] = item
            except (TypeError, json.JSONDecodeError):
                self.error_response = f"Item at index {index} is not a valid dictionary or JSON"
                print(f"check_contents_question_list: FAIL - Invalid dict/JSON at index {index}")
                response["questions"].remove(item)
                continue

        # Remove correct_comments and incorrect_comments if they exist
        item.pop('correct_comments', None)
        item.pop('incorrect_comments', None)

        dict_check = {key: isinstance(item.get(key), expected_keys[key]) for key in expected_keys}
        if all(dict_check.values()):
            status, response = await check_answer(response, index, item)
            if status == "FAIL":
                print(f"check_contents_question_list: FAIL - Answers check failed at index {index}")
                response["questions"].remove(item)
        else:
            self.error_response = f"Item at index {index} is missing required keys or has incorrect types"
            print(f"check_contents_question_list: FAIL - Missing/incorrect keys at index {index}")
            response["questions"].remove(item)

    print("check_contents_question_list: PASS")
    return "PASS", response


async def check_has_key_questions(self, response, validator_status, prompt, action, params):
    """
    ---
    Validation Function 
    ---

    Checks if a llm response is a dictionary with only one key called 'questions'.
    
    ---
    Failure Conditions
    ---

    | Cause of Failure | Failure Mode | Outcome |
    | :--------------- | :----------: | :------ |
    | Response is not a dictionary | Safe | No Effect |
    | Response has no keys | Deadly | LLMResponseError |
    | Response has multiple keys | Safe | New response with all dict values packed in a list and assigned to the key 'questions' |
    | Response has one key != 'questions | Safe | Key reassigned to 'questions', value unchanged |
    """
    # if the response is not a dictionary this function cannot process it
    if not isinstance(response, dict):
        self.error_response = "Response is not a dictionary"
        print("check_has_key_questions: FAIL - Response is not a dictionary")
        return "FAIL", response

    keys = list(response.keys())
    key_length = len(keys)

    if key_length < 1:
        self.error_response = "Response contains no keys"
        print("check_has_key_questions: FAIL - No keys in response")
        raise LLMResponseError(
            message="Response contains no values", 
            action="questions", 
            status_code=500, 
            llm_response=response, 
            failed_validators=[str(validator) for validator in validator_status if validator.status == 'FAIL']
        )

    if key_length > 1:
        new_response = []
        for val in response.values():
            if isinstance(val, list):
                new_response.extend(val)
            else:
                new_response.append(val)

        self.error_response = f"Expected LLM response with single key: 'questions'. Received multiple keys: {keys}. Reassigned response values to dict with key 'questions'"
        print(f"check_has_key_questions: FAIL - Multiple keys {keys}")
        return "FAIL", {"questions": new_response}

    if "questions" not in keys:
        self.error_response = f"Expected LLM response with single key: 'questions'. Received key: {keys[0]}. Reassigned to dict with key 'questions'"
        print(f"check_has_key_questions: FAIL - Key not 'questions': {keys[0]}")
        return "FAIL", {"questions": response[keys[0]]}

    print("check_has_key_questions: PASS")
    return "PASS", response