import logging
import requests
import datetime
import json
import config

from get_myfitness_users import MyfitnessUsers

class MyfitnessData:

    def __init__(self) -> None:

        self.base_url =  config.base_url
        self.base_id = config.base_id
        self.api_key = config.api_key        
        self.fitness_base_name = config.fitness_base_name
        self.fitness_base_cols = config.fitness_base_cols
        self.interval = config.interval 


    def check_for_update(self,date,id):
       
        res = None
        
        try:
            url = f"{self.base_url}/{self.base_id}/{self.fitness_base_name}"
            # query_params = "?filterByFormula=AND({day}='"+date+"',{user_apps_id}='"+str(id)+"')"  
            query_params = "?filterByFormula=({day}='"+str(date)+"')"           

            headers = { 'Authorization': f'Bearer {self.api_key}'}

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



    def prepare_airtable_data(self,app_id,day_,day_data):
        body = {'fields':{}}          
        
        user_apps_id = [f'{app_id}']
        day = f'{day_}'
        net_carbs = day_data.get('carbohydrates',0)
        protein = day_data.get('protein',0)
        total_fat_consumption = day_data.get('fat',0)
        sugar = day_data.get('sugar',0)
        sodium = day_data.get('sodium',0)
        total_calorie = day_data.get('calories',0) 

        
        fields_dict = dict.fromkeys(self.fitness_base_cols,'')
        for key in fields_dict:
            try:
                fields_dict[key] = eval(key)
            except NameError:
                fields_dict[key] = None
            except Exception as e:
                logging.exception(f'error in preparing the data : {e}')


        body['fields'] = fields_dict  
        
        return body


    def get_myfitnesspal_Data(self,users):
       
        today = datetime.datetime.now().date().today()        
        req_body = {'records':[]}

        try:
            for i in  range(0,self.interval):

                day = today- datetime.timedelta(days=i)

                for user in users:                    
                    username = user[0]
                    password = user[1]
                    app_id = user[2]
                    # id = user[3]
                    
                    logging.info(f'processing for : {username} - on - {day}' )

                    client = MyfitnessUsers().get_myfitnesspal_client(username,password) 

                    if not client:
                        continue  
                    
                    day_data = client.get_date(day)  

                    if day_data.totals.get('calories',0) == 0:
                        logging.info(f'No data in food diary on {day} for user : {username}')
                        continue                      
                    
                    record= self.prepare_airtable_data(app_id,day,day_data.totals) 
                    
                    res = self.check_for_update(day,'')  
                    if res:
                        id = res['records'][0]['id']                    
                        logging.info(f'Record exist for the day -{day}, hence updating.')                              
                        self.update_data_in_airtable(id,record)
                        continue    
                      
                    req_body['records'].append(record)
                    
                    

        except Exception as e:
            logging.exception(f'error in getting myfitnesspal data : {e}')
        
        return req_body   

    
    def update_data_in_airtable(self,id,req_body): 
   
        messsage = None
        
        try:
            url = f'{self.base_url}/{self.base_id}/{self.fitness_base_name}/{id}'
            headers = { 'Authorization': f'Bearer {self.api_key}',
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
    

    def insert_data_to_airtable(self,req_body):   
        messsage = None
        
        try:
            url = f'{self.base_url}/{self.base_id}/{self.fitness_base_name}'
            headers = { 'Authorization': f'Bearer {self.api_key}',
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
        users = MyfitnessUsers().get_myfitnesspal_userinfo()    
        req_body = self.get_myfitnesspal_Data(users) 
        res = self.insert_data_to_airtable(req_body)                
        return res



# fitness_obj =  MyfitnessData()
# fitness_obj.main()  