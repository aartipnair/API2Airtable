import logging
import requests
import datetime
import json
import config


class RescuetimeSummary:

    def __init__(self) -> None:

        self.app_name = config.app_name
        self.base_url =  config.base_url
        self.base_id = config.base_id
        self.airtable_api_key = config.airtable_api_key
        self.user_base_name = config.user_base_name
        self.rescuetime_base_name = config.rescuetime_summary_base
        self.rescuetime_base_cols = config.rescuetime_summary_cols
        self.rescuetime_baseurl = config.rescuetime_baseurl
        self.rescuetime_endpoint = config.rescuetime_summary_endpoint
       

    def get_rescuetime_userinfo(self):
        users = []  
        
        try:
            url = f"{self.base_url}/{self.base_id}/{self.user_base_name}"
            query_params = "?filterByFormula=({app_name}='"+self.app_name+"')"

            headers = { 'Authorization': f'Bearer {self.airtable_api_key}'}

            response = requests.request("GET", url+query_params, headers=headers)

            if response.status_code == 200:
                res = response.json() 
               
                for rec in res['records']:                                
                    
                    if 'user_first_name' in rec['fields']:                                   
                        rescuetime_api_key = rec['fields']['api_key']
                        username = rec['fields']['user_first_name'][0]
                        app_id = rec['id']
                        users.append((username,rescuetime_api_key,app_id))
                    else:
                        continue
            else:            
                print(response.text)
        
        except Exception as e:
            logging.exception(f'error in getting the creds : {e}')

        return users


    def get_rescuetime_api_data(self,apikey):    

        try:
            
            url = self.rescuetime_baseurl+self.rescuetime_endpoint
            query_params = f"?key={apikey}"

            response = requests.request("GET", url+query_params)

            if response.status_code == 200:
                return response.json() 
            else:
                print(response.text)
        except Exception as e:
            logging.exception(f' rror in getting rescue time api data : {e}')
            return None


    def check_for_update(self,id):
       
        res = None
        
        try:
            url = f"{self.base_url}/{self.base_id}/{self.rescuetime_base_name}"
            query_params = "?filterByFormula=({id}='"+str(id)+"')"            

            headers = { 'Authorization': f'Bearer {self.airtable_api_key}'}

            response = requests.request("GET", url+query_params, headers=headers)

            if response.status_code == 200:
                result = response.json()
                if result['records']:
                    res = result
                else:
                    res = None      
                
            else:  
                res = None          
                logging.error(response.text)
        
        except Exception as e:
            logging.exception(f'error  : {e}')

        return res


    def prepare_airtable_data(self,app_id,rows):
        req_body = {'records':[]}                
        
        for row in rows:
            row['user_apps_id'] = [app_id]
            id = row.get('id',None)
            day = row.get('date',None)
            res = self.check_for_update(id)
            if res:
                logging.error(f'Record exist for id {id} for the day -{day}, hence skipping.')
                continue 
            
            body ={'fields':{}}
            for key in self.rescuetime_base_cols:
                body['fields'][key] = row.get(key,None)    
           
            req_body['records'].append(body)        
        
        return req_body


    def update_rescuetime_Data(self,users):

        res = None

       
        try:            

            for user in users:                    
                username = user[0]
                rescuetime_api_key = user[1]
                app_id = user[2]               

                rescuetime_data = self.get_rescuetime_api_data(rescuetime_api_key)
                
                if not rescuetime_data:
                    logging.error(f'No data from daily summary api for user : {username}')
                    continue

                req_body= self.prepare_airtable_data(app_id,rescuetime_data)  
                
                logging.info(f"{username} : processing {len(rescuetime_data)}/{len(req_body['records'])} ")                 
                 
                res =self.insert_data_to_airtable(req_body)  
        except Exception as e:
            logging.exception(f'error : {e}')
    
        return res


    def insert_data_to_airtable(self,req_body):   
        messsage = None
        
        try:
            url = f'{self.base_url}/{self.base_id}/{self.rescuetime_base_name}'
            headers = { 'Authorization': f'Bearer {self.airtable_api_key}',
                            'Content-Type': 'application/json'
                            }
            
            if len(req_body['records'])>10:
                index = 10
                for i in range(0,len(req_body['records']),10):               
                        
                    temp = {'records':req_body['records'][i:index]}                 

                    response = requests.request("POST", url, headers=headers, data=json.dumps(temp))

                    if response.status_code == 200:
                        messsage = f'Updated successfully.'
                        logging.info(messsage)            
                        
                    else:
                        messsage = f'Could not update Airtable : {response.text}'
                        logging.error(messsage) 
                    index = index+10    
            else:
                response = requests.request("POST", url, headers=headers, data=json.dumps(req_body))

                if response.status_code == 200:
                    messsage = f'Updated successfully.'
                    logging.info(messsage)            
                    
                else:
                    messsage = f'Could not update Airtable : {response.text}'
                    logging.error(messsage) 
      
                
        except Exception as e:
            logging.exception(f'error in inserting data : {e}')
        return messsage

    def main(self):
        users = self.get_rescuetime_userinfo()   
        res = self.update_rescuetime_Data(users)
                        
        return res

rescuetime_obj = RescuetimeSummary()
rescuetime_obj.main()
