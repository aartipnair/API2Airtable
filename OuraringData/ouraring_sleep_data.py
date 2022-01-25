import logging
import requests
import datetime
import json
import config


class OuraringSleep:

    def __init__(self) -> None:

        self.app_name = config.app_name
        self.base_url =  config.base_url
        self.base_id = config.base_id
        self.airtable_api_key = config.airtable_api_key
        self.user_base_name = config.user_base_name
        self.ouraring_sleep_base_name = config.ouraring_sleep_base_name
        self.ouraring_sleep_base_cols = config.ouraring_sleep_base_cols
        self.ouraring_baseurl = config.ouraring_baseurl
        self.ouraring_sleep_endpoint = config.ouraring_sleep_endpoint
        self.interval = config.interval
       

    def get_ouraring_userinfo(self):
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
                        ouraring_api_key = rec['fields']['api_key']
                        username = rec['fields']['user_first_name'][0]
                        app_id = rec['id']
                        users.append((username,ouraring_api_key,app_id))
                    else:
                        continue
            else:            
                print(response.text)
        
        except Exception as e:
            logging.exception(f'error in getting the creds : {e}')

        return users


    def get_ouraring_api_data(self,apikey):    

        try:
            end_date = datetime.datetime.now().date().today()   
            start_date = end_date- datetime.timedelta(days=self.interval)      
            
            url = self.ouraring_baseurl+self.ouraring_sleep_endpoint

            query_params = f"?start={start_date}&end={end_date}"

            headers = {'Authorization': f'Bearer {apikey}'}

            response = requests.request("GET", url+query_params, headers=headers)

            if response.status_code == 200:
                return response.json() 
            else:
                print(response.text)
        except Exception as e:
            logging.exception(f'Error in getting ouraring api data : {e}')
            return None


    def check_for_update(self,date,id):
       
        res = None
        
        try:
            url = f"{self.base_url}/{self.base_id}/{self.ouraring_sleep_base_name}"
            query_params = "?filterByFormula=AND({summary_date}='"+date+"',{period_id}='"+str(id)+"')"              

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
            period_id = row.get('period_id',None)
            day = row.get('summary_date',None)            
            
            body ={'fields':{}}
            for key in self.ouraring_sleep_base_cols:

                value = row.get(key,None)
                if isinstance(value, list):
                    if key in ('user_apps_id'):
                        body['fields'][key] = value
                        continue
                    value= str(row.get(key,None))
                body['fields'][key] = value

            res = self.check_for_update(day,period_id)
            if res:
                id = res['records'][0]['id']                    
                logging.error(f'Record exist for the day -{day}, hence updating.')                              
                self.update_data_in_airtable(id,body)                                
            else: 
           
                req_body['records'].append(body)            
     
        return req_body


    def update_ouraring_Data(self,users):

        res = None
       
        try:            

            for user in users:                    
                username = user[0]
                ouraring_api_key = user[1]
                app_id = user[2]               

                ouraring_data = self.get_ouraring_api_data(ouraring_api_key)
                
                if not ouraring_data['sleep']:
                    logging.error(f'No data from sleep api for user : {username}')
                    continue

                req_body= self.prepare_airtable_data(app_id,ouraring_data['sleep'])  
                # print(req_body)
                
                logging.info(f"{username} : processing {len(ouraring_data['sleep'])}/{len(req_body['records'])} ")                 
                 
                res =self.insert_data_to_airtable(req_body)  
        except Exception as e:
            logging.exception(f'error : {e}')
    
        return res


    def insert_data_to_airtable(self,req_body): 
        messsage = None
        
        try:
            url = f'{self.base_url}/{self.base_id}/{self.ouraring_sleep_base_name}'
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
                # print(json.dumps(req_body))
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

    def update_data_in_airtable(self,id,req_body): 
        messsage = None
        
        try:
            url = f'{self.base_url}/{self.base_id}/{self.ouraring_sleep_base_name}/{id}'
            headers = { 'Authorization': f'Bearer {self.airtable_api_key}',
                            'Content-Type': 'application/json'                            }
            
   
            response = requests.request("PUT", url, headers=headers, data=json.dumps(req_body))

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
        users = self.get_ouraring_userinfo()   
        res = self.update_ouraring_Data(users)
                        
        return res

sleep_obj = OuraringSleep()
sleep_obj.main()
