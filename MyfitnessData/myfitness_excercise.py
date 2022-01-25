import logging
import requests
import datetime
import json
import config

from get_myfitness_users import MyfitnessUsers

class MyfitnessExcercise:

    def __init__(self) -> None:

        self.base_url =  config.base_url
        self.base_id = config.base_id
        self.api_key = config.api_key        
        self.excercise_base_name = config.excercise_base_name
        self.excercise_base_cols = config.excercise_base_cols
        self.interval = config.interval 


    def check_for_update(self,date,type,name):
       
        res = None
        
        try:
            url = f"{self.base_url}/{self.base_id}/{self.excercise_base_name}"
            query_params = "?filterByFormula=AND({day}='"+str(date)+"',{excercise_type}='"+type+"',{name}='"+name+"')"  
            # query_params = "?filterByFormula=({day}='"+str(date)+"')"           

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




    def get_myfitnesspal_Data(self,users):
       
        today = datetime.datetime.now().date().today()        
        

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

                    cardio_data = day_data.exercises[0].get_as_list()
                    strength_data = day_data.exercises[1].get_as_list()


                    # print(day_data.exercises[0].get_as_list()) 
                    # print(day_data.exercises[1].get_as_list()) 

                    if not cardio_data  and not strength_data:
                        logging.info(f'No excercise on {day} for user : {username}')
                        continue                      
                    
                    if not cardio_data:
                        logging.info(f'No cardio excercise on {day} for user : {username}')

                    else:
                        logging.info(f'Processing cardio')
                        self.process_cardio(app_id,day,cardio_data)

                    if not strength_data:
                        logging.info(f'No strength excercise on {day} for user : {username}')
                    else:
                        logging.info(f'Processing strength')
                        self.process_strength(app_id,day,strength_data)



        except Exception as e:
            logging.exception(f'error in getting myfitnesspal data : {e}')
        
        return 

    
    def process_cardio(self, app_id,day_,cardio_data):
        req_body = {'records':[]}
        # if not cardio_data:
        #     return None
    
        for data in cardio_data:
            body = {'fields':{}}  
            user_apps_id = [f'{app_id}']
            day = f'{day_}'
            excercise_type = 'cardio' 
            name = data.get('name',0)
            minutes = data.get('nutrition_information','').get('minutes',0)
            calories_burned = data.get('nutrition_information','').get('calories burned',0)
                    
            fields_dict = dict.fromkeys(self.excercise_base_cols,'')
            for key in fields_dict:
                try:
                    fields_dict[key] = eval(key)
                except NameError:
                    fields_dict[key] = None
                except Exception as e:
                    logging.exception(f'error in preparing the cardio data : {e}')


            body['fields'] = fields_dict 
            res = self.check_for_update(day,excercise_type,name)  
            if res:
                id = res['records'][0]['id']                    
                logging.info(f'Cardio : Record exist for the day -{day}, hence updating.')                              
                self.update_data_in_airtable(id,body)
                continue     
            req_body['records'].append(body)

        print(req_body)
        res = self.insert_data_to_airtable(req_body)
            
        logging.info('Cardio data updated successfully.')


    def process_strength(self, app_id,day_,strength_data):
        req_body = {'records':[]}
        # if not cardio_data:
        #     return None
    
        for data in strength_data:
            body = {'fields':{}}  
            user_apps_id = [f'{app_id}']
            day = f'{day_}'
            excercise_type = 'strength' 
            name = data.get('name','')
            sets = data.get('nutrition_information','').get('sets',0)
            reps = data.get('nutrition_information','').get('reps/set',0)
            weight = data.get('nutrition_information','').get('weight/set',0)
                    
            fields_dict = dict.fromkeys(self.excercise_base_cols,'')
            for key in fields_dict:
                try:
                    fields_dict[key] = eval(key)
                except NameError:
                    fields_dict[key] = None
                except Exception as e:
                    logging.exception(f'error in preparing the cardio data : {e}')


            body['fields'] = fields_dict 
            res = self.check_for_update(day,excercise_type,name)  
            if res:
                id = res['records'][0]['id']                    
                logging.info(f'Strength : Record exist for the day -{day}, hence updating.')                              
                self.update_data_in_airtable(id,body)
                continue     
            req_body['records'].append(body)
        print(req_body)
        res = self.insert_data_to_airtable(req_body)
            
        logging.info('Strength data updated successfully.')


    def update_data_in_airtable(self,id,req_body): 
   
        messsage = None
        
        try:
            url = f'{self.base_url}/{self.base_id}/{self.excercise_base_name}/{id}'
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
            url = f'{self.base_url}/{self.base_id}/{self.excercise_base_name}'
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
        self.get_myfitnesspal_Data(users) 
        # res = self.insert_data_to_airtable(req_body)                
        return 'Successfull'




# fitness_obj =  MyfitnessExcercise()
# fitness_obj.main()  