import os 

# rescuetime app config

app_name = 'rescue time'

airtable_api_key = 'keyOgopuDbcU5fql5'
base_url= 'https://api.airtable.com/v0'

base_id = 'appXsczppOity0AP7'

user_base_name = 'user apps'


rescuetime_base_name = 'rescuetime'

rescuetime_base_cols = ['user_apps_id','date_time','Time_Spent_seconds','Number_of_People','Activity',
                        'Document','Category','Productivity']

rescuetime_baseurl = 'https://www.rescuetime.com/anapi'
rescuetime_endpoint = '/data'

restrict_interval = 1

##daily summary
rescuetime_summary_endpoint = '/daily_summary_feed'
rescuetime_summary_base = 'rescuetime-summary'

rescuetime_summary_cols = ['id','date','productivity_pulse','very_productive_percentage','productive_percentage','neutral_percentage',
                           'distracting_percentage','very_distracting_percentage','all_productive_percentage','all_distracting_percentage',
                           'uncategorized_percentage','business_percentage','communication_and_scheduling_percentage',
                           'social_networking_percentage','design_and_composition_percentage','entertainment_percentage','news_percentage',
                           'software_development_percentage','reference_and_learning_percentage','shopping_percentage','utilities_percentage',
                           'total_hours','very_productive_hours','productive_hours','neutral_hours','distracting_hours',
                           'very_distracting_hours','all_productive_hours','all_distracting_hours','uncategorized_hours','business_hours',
                           'communication_and_scheduling_hours','social_networking_hours','design_and_composition_hours','entertainment_hours',
                           'news_hours','software_development_hours','reference_and_learning_hours','shopping_hours','utilities_hours',
                           'total_duration_formatted','very_productive_duration_formatted','productive_duration_formatted',
                           'neutral_duration_formatted','distracting_duration_formatted','very_distracting_duration_formatted',
                           'all_productive_duration_formatted','all_distracting_duration_formatted','uncategorized_duration_formatted',
                           'business_duration_formatted','communication_and_scheduling_duration_formatted',
                           'social_networking_duration_formatted','design_and_composition_duration_formatted',
                           'entertainment_duration_formatted','news_duration_formatted','software_development_duration_formatted',
                           'reference_and_learning_duration_formatted','shopping_duration_formatted','utilities_duration_formatted',
                           'user_apps_id']

