import logging
import requests
import datetime
import json
import config

from get_myfitness_users import MyfitnessUsers

class MyfitnessMeal:

    def __init__(self) -> None:

        self.base_url =  config.base_url
        self.base_id = config.base_id
        self.api_key = config.api_key        
        self.meals_base_name = config.meals_base_name
        self.meals_base_cols = config.meals_base_cols
        self.interval = config.interval 


    def check_for_update(self,date,meal,name):
       
        res = None
        
        try:
            url = f"{self.base_url}/{self.base_id}/{self.meals_base_name}"
            # query_params = '?filterByFormula=AND({day}='"+str(date)+"',{meal}='"+meal+"',{name}='"+name+"')"  
            # query_params = "?filterByFormula=({day}='"+str(date)+"')"           
            query_params = '?filterByFormula=AND({day}="'+str(date)+'",{meal}="'+meal+'",{name}="'+name+'")'
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
                    # print(username)
                    logging.info(f'processing for : {username} - on - {day}' )

                    client = MyfitnessUsers().get_myfitnesspal_client(username,password) 

                    if not client:
                        continue  
                    
                    day_data = client.get_date(day) 

                    breakfast = day_data.meals[0].get_as_list()
                    
                    lunch = day_data.meals[1].get_as_list()
                   
                    dinner = day_data.meals[2].get_as_list()
                  
                    snacks = day_data.meals[3].get_as_list()                  
                   

                    if not breakfast  and not lunch and not dinner and not snacks:
                        logging.info(f'No meals updated on {day} for user : {username}')
                        continue                      
                    
                    self.process_meal(app_id,day,'Breakfast',breakfast) if breakfast else \
                         logging.info(f'No breakfast data on {day} for user : {username}')

                    self.process_meal(app_id,day,'Lunch',lunch) if lunch else \
                         logging.info(f'No lunch data on {day} for user : {username}')

                    self.process_meal(app_id,day,'Dinner',dinner) if dinner else \
                         logging.info(f'No dinner data on {day} for user : {username}')

                    self.process_meal(app_id,day,'Snacks',snacks) if snacks else \
                         logging.info(f'No snacks data on {day} for user : {username}')
                   

        except Exception as e:
            logging.exception(f'error in getting myfitnesspal data : {e}')
        
        return 

    
    def process_meal(self, app_id,day_,meal_type,data_list):
        req_body = {'records':[]}
        # if not cardio_data:
        #     return None
    
        for data in data_list:
            body = {'fields':{}}  
            user_apps_id = [f'{app_id}']
            day = f'{day_}'
            meal = meal_type
            name = data.get('name','')
            calories = data.get('nutrition_information','').get('calories',0)
            carbohydrates = data.get('nutrition_information','').get('carbohydrates',0)
            fat = data.get('nutrition_information','').get('fat',0)
            protein = data.get('nutrition_information','').get('protein',0)
            sodium = data.get('nutrition_information','').get('sodium',0)
            sugar = data.get('nutrition_information','').get('sugar',0)

            fields_dict = dict.fromkeys(self.meals_base_cols,'')
            for key in fields_dict:
                try:
                    fields_dict[key] = eval(key)
                except NameError:
                    fields_dict[key] = None
                except Exception as e:
                    logging.exception(f'error in preparing the cardio data : {e}')


            body['fields'] = fields_dict 
            res = self.check_for_update(day,meal_type,name)  
            if res:
                id = res['records'][0]['id']                    
                logging.info(f'Cardio : Record exist for the day -{day}, hence updating.')                              
                self.update_data_in_airtable(id,body)
                continue     
            req_body['records'].append(body)

        print(req_body)
        res = self.insert_data_to_airtable(req_body)
            
        logging.info('Data updated successfully.')
  


    def update_data_in_airtable(self,id,req_body): 
   
        messsage = None
        
        try:
            url = f'{self.base_url}/{self.base_id}/{self.meals_base_name}/{id}'
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
            url = f'{self.base_url}/{self.base_id}/{self.meals_base_name}'
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
                     
        return 'Successfull'



# fitness_obj =  MyfitnessMeal()
# fitness_obj.main()  