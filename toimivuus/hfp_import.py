import argparse
import dotenv
import logging
import os
import toimivuus
from typing import List


def main(datehours: List[str],
         events: List[str],
         routes: List[str],
         loglvl: str):
    
    logging.basicConfig(level=getattr(logging, loglvl))
    logging.info(datehours)
    logging.info(events)
    logging.info(routes)
    logging.info(os.getenv('HFP_STORAGE_CONNECTION_STRING'))
    logging.info(os.getenv('HFP_STORAGE_CONTAINER_NAME'))
    
    for dh in datehours:
        rhd = toimivuus.RawHfpDump(dump_date_hour = dh,
                                   event_types = events)
        for rhf in rhd.raw_hfp_files:
            print(f'{rhf.raw_file_name} {rhf.remote_exists()}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import raw HFP data.')
    parser.add_argument('--datehours',
                        help='Date-hour strings to import data from, e.g. 2020-12-01T06 2020-12-01T07.',
                        nargs='+',
                        required=True)
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
    
    main(args.datehours, args.events, args.routes, args.loglvl)