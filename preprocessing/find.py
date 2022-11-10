from pandas import DataFrame, read_csv, to_datetime
from pathlib import Path
from preprocessing import query
from datetime import datetime
from vssutils import LocalSecrets


# Camera positions
"""
Ballast Left
Ballast Left Inside
Ballast Left Outside
Ballast Right
Ballast Right Inside
Ballast Right Outside
Rail Left Inside
Rail Left Outside
Rail Left Top
Rail Right Inside
Rail Right Outside
Rail Right Top
Train Back
Train Front
"""


def turnout(secrets: LocalSecrets, equipment: int = 0, geocode: int = 0, switch_name: str = '', date: str = '0001-01-01',
            mode: str = 'closest_before', new: bool = True) -> DataFrame:
    """
    Finds images of a turnout based on geocode + switch name or based on equipment number. If no date is given, the
    most recent available image will be provided. If a date is provided a mode can be specified. If no mode is
    specified, the mode 'closest_before' will be executed. Modes:
    'closest_before'    provide the images closest before the given date (i.e. last picture before fracture date)
    'closest'           provide the images closest to the given date (i.e. picture closest to a certain tonnage)

    A bool 'new' can be provided to either:
     keep working with the current csv that was queried from Azure if False
     query a new table from azure which is stored in csv if True
    """
    filepath = Path('O:/outputs/temp.csv')
    if equipment != 0:
        geocode, switch_name = _geocode_and_switch_name(equipment)
    elif geocode != 0 and switch_name != '':
        pass
    else:
        raise NotImplementedError(f'Unsupported input for find.py' +
                                  f'Only the modes \'closest_before\' and \'closest\' are currently supported.')

    # Query from Azure
    if new:
        query_result = query.geocode_and_switch_name(secrets, geocode, switch_name)
        query_result.to_csv(index=False, path_or_buf=filepath, sep=';', decimal=',')
    query_result = read_csv(filepath, delimiter=';', decimal=',')

    # Filter based on wishes
    if date == datetime.strptime('0001-01-01', '%Y-%m-%d'):  # most recent images
        most_recent = datetime.strptime(query_result.sort_values('recording_date')['recording_date'].unique()[-1],
                                        '%Y-%m-%d')
        query_result['recording_date'] = to_datetime(query_result['recording_date'], format='%Y-%m-%d')
        return query_result[query_result['recording_date'] - most_recent == most_recent - most_recent]

    elif mode in ['closest_before', 'closest']:  # correct mode provided
        date = datetime.strptime(date, '%Y-%m-%d')
        query_result['recording_date'] = to_datetime(query_result['recording_date'], format='%Y-%m-%d')

        if mode == 'closest_before':  # images closest before the given date
            before = query_result[query_result['recording_date'] < date]
            closest_before = before.iloc[(date - before['recording_date']).argsort()[:1]].squeeze()['recording_date']
            return before[before['recording_date'] - closest_before == closest_before - closest_before]

        elif mode == 'closest':  # images closest to the given date
            closest = query_result.iloc[(query_result['recording_date'] - date).abs().argsort()[:1]]\
                .squeeze()['recording_date']
            return query_result[query_result['recording_date'] - closest == closest - closest]

    else:
        raise NotImplementedError(f'Provided unsupported value for the \'mode\' variable: {mode}.\n' +
                                  f'Only the modes \'closest_before\' and \'closest\' are currently supported.')


def _geocode_and_switch_name(equipment: int) -> (int, str):
    paths = [Path('./data/informatieportaal_wissels_20221109.csv'),
             Path('./data/informatieportaal_wissels_20211228.csv'),
             Path('./data/informatieportaal_wissels_20221025.csv'),
             Path('./data/informatieportaal_kruisingen_20210209.csv'),
             Path('./data/informatieportaal_kruisingen_20221025.csv')]
    for path in paths:
        turnouts = read_csv(path, delimiter=';')
        turnouts = turnouts[turnouts['equipment'] == equipment]
        if len(turnouts) == 1:
            turnout = turnouts.squeeze()
            return int(turnout.geoCode), turnout.naam
    raise NotImplementedError(f'Did not find equipment {equipment}')
