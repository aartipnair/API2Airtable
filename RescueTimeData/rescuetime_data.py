import logging
import requests
import datetime
import json
import config


class RescuetimeData:

    def __init__(self) -> None:

        self.app_name = config.app_name
        self.base_url =  config.base_url
        self.base_id = config.base_id
        self.airtable_api_key = config.airtable_api_key
        self.user_base_name = config.user_base_name
        self.rescuetime_base_name = config.rescuetime_base_name
        self.rescuetime_base_cols = config.rescuetime_base_cols
        self.rescuetime_baseurl = config.rescuetime_baseurl
        self.rescuetime_endpoint = config.rescuetime_endpoint
        self.restrict_interval = config.restrict_interval

        

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


    def get_rescuetime_api_data(self,apikey,restrict_begin,restrict_end):    

        try:
            
            url = self.rescuetime_baseurl+self.rescuetime_endpoint
            query_params = f"?key={apikey}&perspective=interval&\
                            resolution_time=hour&restrict_kind=document&restrict_begin={restrict_begin}\
                                &restrict_end={restrict_end}&format=json"

            response = requests.request("GET", url+query_params)

            if response.status_code == 200:
                return response.json() 
            else:
                print(response.text)
        except Exception as e:
            logging.exception(f' rror in getting rescue time api data : {e}')
            return None


    def prepare_airtable_data(self,app_id,rows):
        req_body = {'records':[]}         
        user_apps_id  = [f'{app_id}']         
        
        for row in rows:
            
            body ={'fields':{}}
            date_time = f'{row[0]}'
            Time_Spent_seconds = row[1]
            Number_of_People = row[2]
            Activity = f'{row[3]}'
            Document = f'{row[4]}'
            Category = f'{row[5]}'
            Productivity = row[6] 

            fields_dict = dict.fromkeys(self.rescuetime_base_cols,'')
            for key in fields_dict:
                try:
                    fields_dict[key] = eval(key)
                except NameError:
                    fields_dict[key] = None
                except Exception as e:
                    logging.exception(f'error in preparing the data : {e}')

            body['fields'] = fields_dict 
            req_body['records'].append(body)          
         
        
        return req_body


    def update_rescuetime_Data(self,users):

        res = None

        restrict_end = datetime.datetime.now().date().today()            

        try:            

            restrict_begin = restrict_end- datetime.timedelta(days=self.restrict_interval)

            for user in users:                    
                username = user[0]
                rescuetime_api_key = user[1]
                app_id = user[2]               

                rescuetime_data = self.get_rescuetime_api_data(rescuetime_api_key,restrict_begin,restrict_end)
                
                if not rescuetime_data:
                    logging.error(f'No data from - {restrict_begin} - to - {restrict_end} for user : {username}')
                    continue

                req_body= self.prepare_airtable_data(app_id,rescuetime_data['rows'])  
                print(f"{username} : processing {len(rescuetime_data['rows'])}/{len(req_body['records'])} - from - {restrict_begin} - to - {restrict_end}")
                logging.info(f"{username} : processing {len(rescuetime_data['rows'])}/{len(req_body['records'])} - from - {restrict_begin} - to - {restrict_end}")                 
                 
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

rescuetime_obj = RescuetimeData()
rescuetime_obj.main()
