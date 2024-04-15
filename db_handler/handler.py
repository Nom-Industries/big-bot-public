from constants import NAME_TO_SCHEMA
import requests

API_ADDRESS = ""

class Handler:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_data(self, table: str, **query):
        query_req = f"{NAME_TO_SCHEMA[table][0]}?" + '&'.join([i + "=" + str(query[i]) for i in query])

        data = requests.get(f"http://{API_ADDRESS}" + query_req + f"&api_key={self.api_key}").json()

        if "error" in data:
            return False     

        return [NAME_TO_SCHEMA[table][1](**i) for i in data]
    
    def create_data(self, table: str, **data):
        if not table == "application_questions" and not table == "logging" and not table == "suggestions_info":
            for i in data:
                if isinstance(data[i], list):
                    data[i] = str(data[i])
        
        req = requests.post(f"http://{API_ADDRESS}{NAME_TO_SCHEMA[table][0]}?api_key={self.api_key}", json=data) # FIX UPVOTES AND DOWNVOTES NOT ALLOWED TO BE []

        if req.status_code != 201 or "detail" in req.json():
            return False
        
        return NAME_TO_SCHEMA[table][1](**req.json())
    
    def update_data(self, table: str, data):
        data = data.__dict__
        if not table == "application_questions" and not table == "logging" and not table == "suggestions_info":
            for i in data:
                if isinstance(data[i], list):
                    data[i] = str(data[i])

        req = requests.patch(f"http://{API_ADDRESS}{NAME_TO_SCHEMA[table][0]}?api_key={self.api_key}", json=data)


        if req.status_code != 200:
            return False

        return NAME_TO_SCHEMA[table][1](**req.json())
    
    def delete_data(self, table: str, data):
        data = data.__dict__

        if not table == "application_questions" and not table == "logging" and not table == "suggestions_info":
            for i in data:
                if isinstance(data[i], list):
                    data[i] = str(data[i])

        req = requests.delete(f"http://{API_ADDRESS}{NAME_TO_SCHEMA[table][0]}?api_key={self.api_key}", json=data)

        if req.status_code != 204:
            return False

        return True
