from preprocessing import find, query
from figures import visualise

switch_name = '1183'
geocode = 587
run_id = '2022_31'
equipment = 11317242
camera = 'Rail Right Top'
secrets = query.local_secrets()
query_result = find.turnout(secrets, equipment=11317242, date='2021-03-08', mode='closest_before')
query_result.to_csv(index=False, path_or_buf='O:/outputs/temp.csv', sep=';', decimal=',')
visualise.concat_image(secrets, query_result)

# find.turnout(geocode=587, switch_name='1183')
