## myfitness app config

import os 

app_name = os.getenv('app_name','')
api_key = os.getenv('api_key','')
base_url= os.getenv('base_url','')

base_id = os.getenv('base_id','')

user_base_name = os.getenv('user_base_name','')
fitness_base_name = os.getenv('fitness_base_name','')

app_name = 'my fitness pal'

api_key = 'keyOgopuDbcU5fql5'
base_url= 'https://api.airtable.com/v0'

base_id = 'appXsczppOity0AP7'

user_base_name = 'user apps'
fitness_base_name = 'myfitnespal'

fitness_base_cols = ['user_apps_id','day','net_carbs','protein','total_fat_consumption','sugar','sodium','total_calorie']

interval = 5

excercise_base_name = 'myfitness_excercise'
excercise_base_cols = ['user_apps_id','day','excercise_type','name','minutes','calories_burned','sets','reps','weight']


meals_base_name = 'myfitness_meals'
meals_base_cols = ['user_apps_id','day','meal','name','sodium','carbohydrates','calories','fat','sugar','protein']