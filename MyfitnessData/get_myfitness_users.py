import myfitnesspal
import logging
import requests
import json
import config


class MyfitnessUsers:

    def __init__(self) -> None:

        self.app_name = config.app_name
        self.base_url =  config.base_url
        self.base_id = config.base_id
        self.api_key = config.api_key
        self.user_base_name = config.user_base_name   

        

    def get_myfitnesspal_userinfo(self):
        users = []  
        
        try:
            url = f"{self.base_url}/{self.base_id}/{self.user_base_name}"
            query_params = "?filterByFormula=({app_name}='"+self.app_name+"')"

            headers = { 'Authorization': f'Bearer {self.api_key}'}

            response = requests.request("GET", url+query_params, headers=headers)

            if response.status_code == 200:
                res = response.json() 
               
                for rec in res['records']:                                
                    
                    if 'user_name' in rec['fields']:                                   
                        username = rec['fields'].get('user_name','')
                        password = rec['fields'].get('password','')
                        app_id = rec['id']
                        id = rec['fields'].get('user_apps_id','')
                        users.append((username,password,app_id,id))
                    else:
                        continue
            else:            
                logging.error(response.text)
        
        except Exception as e:
            logging.exception(f'error in getting the creds : {e}')

        return users


    def get_myfitnesspal_client(self,username,password):        

        try:
            client = myfitnesspal.Client(username=username, password= password,login=True)
            return client
        except Exception as e:
            logging.exception(f'myfitnesspal client error for username :- {username} : {e}')
            return None
