import json
import re

async def check_valid_json(self, response, validator_status, prompt, action, params):
    try:
        dict_response = json.loads(response)
        print("check_valid_json: PASS")
        return "PASS", dict_response
    except Exception as e:
        print(f"check_valid_json: FAIL - {str(e)}")
        self.error_response = f"Invalid JSON format: {str(e)}"
        return "FAIL", response
    

async def check_valid_json_multi(self, response, validator_status, prompt, action, params):
    try:
        dict_response1 = json.loads(response[0])
        dict_response2 = json.loads(response[1])
        res = dict_response1 | dict_response2
        return "PASS", res
    except Exception as e:
        return "FAIL", response


async def check_is_not_json(self, response, validator_status, prompt, action, params):
    if type(response) == str:
        try:
            dict_response = json.loads(response)
            return "FAIL", dict_response
        except ValueError:
            return "PASS", response
    return "PASS", response


async def check_dict_values_not_json(self, response, validator_status, prompt, action, params):
    new_response = response
    try:
        keys = list(new_response.keys())
    
    except AttributeError:
        self.error_response = "Response not a dict"
        return "FAIL", response
    
    pattern = r'[\[\]]|[\{\}]' 
    status = "PASS"
    error_response = []

    for key in keys:
        val = new_response[key]
        if type(val) == str and re.search(pattern, val):
            try:
                new_response[key] = json.loads(val)
                error_response.append(f"Value at key: {key} matches JSON string and was processed")
                status = "FAIL"

            except ValueError:
                error_response.append(f"Value at key: {key} matches JSON string but is unprocessable")
                status = "FAIL"

    self.error_response = " - ".join(error_response)

    return status, new_response
