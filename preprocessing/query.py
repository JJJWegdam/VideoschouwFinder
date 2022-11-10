from vssutils import VssClient, LocalSecrets
from azure.identity import InteractiveBrowserCredential
from pandas import DataFrame


def geocode_and_switch_name(secrets: LocalSecrets, geocode: int, switch_name: str) -> DataFrame:
    run_id = '2022_31'
    camera = 'Rail Right Top'

    vss_client = VssClient('test', secrets)
    query = f"""SELECT kilometrage, frame_km_direction, x, y, side, camera, frame_index, storage_file_path,
                      run_id, switch_leg_identifier.switch_name, movie.recording_date, geocode, 
                      spoortak_segment.id as segment_id, supplier
                 FROM frame
                 LEFT JOIN spoortak_segment on frame.spoortak_segment_id=spoortak_segment.id
                 LEFT JOIN spoortak_identifier on spoortak_segment.spoortak_id=spoortak_identifier.id
                 LEFT JOIN switch_leg_identifier on spoortak_segment.switch_leg_id=switch_leg_identifier.id
                 LEFT JOIN movie on spoortak_segment.movie_id = movie.id
                 LEFT JOIN track_side on spoortak_segment.track_side_id = track_side.id
                 LEFT JOIN delivery on movie.delivery_id = delivery.id
                     WHERE switch_leg_identifier.switch_name = '{switch_name}'
                     AND geocode = {geocode}
                     AND camera = '{camera}'
                     """.format(switch_name=switch_name, geocode=geocode, run_id=run_id, camera=camera)

    with vss_client.getDbClient() as sut:
        query_result = sut.query(query)
    return query_result


def local_secrets() -> LocalSecrets:
    return LocalSecrets('BH-VSService-Test-KV', InteractiveBrowserCredential())
