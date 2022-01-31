import argparse
import dotenv
import logging
import os
import toimivuus
from typing import List


def main(first_datehour: str,
         last_datehour: str,
         events: List[str],
         routes: List[str],
         loglvl: str):

    logging.basicConfig(level=getattr(logging, loglvl))
    logging.info(first_datehour)
    logging.info(last_datehour)
    logging.info(events)
    logging.info(routes)
    logging.info(os.getenv('HFP_STORAGE_CONNECTION_STRING'))
    logging.info(os.getenv('HFP_STORAGE_CONTAINER_NAME'))

    rhd = toimivuus.RawHfpDump(first_datehour=first_datehour,
                               last_datehour=last_datehour,
                               event_types=events)
    rhd.download_raw_files()
    rhd.make_filtered_dataframes(routes=routes,
                                 columns=['tsi', 'ownerOperatorId', 'veh',
                                          'route', 'dir', 'oday', 'start',
                                          'oper', 'eventType', 'odo', 'drst',
                                          'stop', 'longitude', 'latitude'])
    rhd.create_merged_dataframe()
    print(rhd.dataframe.shape)
    rhd.write_to_csv()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import raw HFP data.')
    parser.add_argument('--first_datehour',
                        help='First date-hour to import data from, e.g. 2020-12-01T06.',
                        required=True)
    parser.add_argument('--last_datehour',
                        help='Last date-hour to import data from, e.g. 2020-12-01T12. If omitted, only first-datehour is imported.')
    parser.add_argument('--events',
                        help='HFP event types to import, e.g. DOO DOC ARR.',
                        nargs='+',
                        required=True)
    parser.add_argument('--routes',
                        help='Route identifiers of trips to import.',
                        nargs='+',
                        required=True)
    parser.add_argument('--loglvl',
                        help='Logging level.',
                        default='WARNING',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    args = parser.parse_args()

    main(args.first_datehour, args.last_datehour,
         args.events, args.routes, args.loglvl)
