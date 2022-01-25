import os 

##ouraring activity summary 

app_name = 'oura ring'

airtable_api_key = 'keyOgopuDbcU5fql5'
base_url= 'https://api.airtable.com/v0'

base_id = 'appXsczppOity0AP7'

user_base_name = 'user apps'


ouraring_base_name = 'ouraring-summary'

interval = 5


ouraring_baseurl = 'https://api.ouraring.com/v1'
ouraring_activity_endpoint = '/activity'

ouraring_base_cols = ['user_apps_id','summary_date','timezone','day_start','day_end','cal_active','cal_total','class_5min','steps',
                      'daily_movement','non_wear','rest','inactive','low','medium','high','inactivity_alerts','average_met','met_1min',
                      'met_min_inactive','met_min_low','met_min_medium','met_min_high','target_calories','target_km','target_miles',
                      'to_target_km','to_target_miles','score','score_meet_daily_targets','score_move_every_hour','score_recovery_time',
                      'score_stay_active','score_training_frequency','score_training_volume','rest_mode_state','total']


ouraring_sleep_base_name = 'ouraring-sleep'
ouraring_sleep_endpoint = '/sleep'
ouraring_sleep_base_cols = ['user_apps_id','summary_date','period_id','is_longest','timezone','bedtime_end','bedtime_start',
                            'breath_average','duration','total','awake','rem',
                            'deep','midpoint_time','efficiency','restless','light','onset_latency',
                            'hr_5min','hr_average','hr_lowest',
                            'hypnogram_5min','rmssd','rmssd_5min','score','score_alignment',
                            'score_deep','score_disturbances','score_efficiency','score_latency','score_rem','score_total',
                            'temperature_deviation','temperature_trend_deviation','bedtime_start_delta','bedtime_end_delta',
                            'midpoint_at_delta','temperature_delta']


ouraring_readiness_base_name = 'ouraring-readiness'
ouraring_readiness_endpoint = '/readiness'
ouraring_readiness_base_cols = ['user_apps_id','summary_date','period_id','score','score_activity_balance','score_hrv_balance',
                                'score_previous_day','score_previous_night','score_recovery_index','score_resting_hr',
                                'score_sleep_balance','score_temperature','rest_mode_state']


ouraring_activity_base_name = 'ouraring-activity'
ouraring_activity_endpoint = '/activity'
ouraring_activity_base_cols = ['user_apps_id','summary_date','timezone','day_start','day_end','cal_active','cal_total',
                                'class_5min','steps','daily_movement','non_wear','rest','inactive','low','medium','high',
                                'inactivity_alerts','average_met','met_1min','met_min_inactive','met_min_low','met_min_medium',
                                'met_min_high','target_calories','target_km','target_miles','to_target_km','to_target_miles',
                                'score','score_meet_daily_targets','score_move_every_hour','score_recovery_time',
                                'score_stay_active','score_training_frequency','score_training_volume','rest_mode_state','total']