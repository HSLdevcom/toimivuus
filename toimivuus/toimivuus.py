import io
import logging as log
import os
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List

import pandas
import zstandard
from azure.storage.blob import BlobServiceClient, ContainerClient


def cached_file_path(fname: str) -> str:
    """Append fname to DATA_CACHE_DIRECTORY."""
    cache = os.getenv('DATA_CACHE_DIRECTORY')
    return os.path.join(cache, fname)

def datehour_range(start: datetime, end: datetime):
    """Generate dates and hours between (inclusive) start and end."""
    current_datehour: datetime = start
    while current_datehour <= end:
        yield current_datehour
        current_datehour += timedelta(hours=1)

class EventType(Enum):
    """HFP event type labels,
    see https://digitransit.fi/en/developers/apis/4-realtime-api/vehicle-positions/#event-types"""
    VP = auto()
    DUE = auto()
    ARR = auto()
    DEP = auto()
    ARS = auto()
    PDE = auto()
    PAS = auto()
    WAIT = auto()
    DOO = auto()
    DOC = auto()
    TLR = auto()
    TLA = auto()
    DA = auto()
    DOUT = auto()
    BA = auto()
    BOUT = auto()
    VJA = auto()
    VJOUT = auto()

class RawHfpFile:
    """Points to a file of raw HFP messages of single type received an hour.
    To operate with remote raw data file, container_client must be provided."""

    REQUEST_TIMEOUT_S=2

    def __init__(self, base_name: str, event_type: EventType):
        self.raw_file_name = f'{base_name}_{event_type.name}.csv.zst'
        self.local_path = cached_file_path(self.raw_file_name)
        self.dataframe: pandas.DataFrame = None
    
    def remote_exists(self) -> bool:
        return self.blob_client is not None and self.blob_client.exists()

    def local_exists(self) -> bool:
        """Does the target file exist in local cache?"""
        return os.path.exists(self.local_path)

    def download_remote(self, container_client: ContainerClient) -> None:
        """Download target blob in remote container to local cache."""
        if self.local_exists():
            log.info(f'{self.raw_file_name} already exists, skipping download')
            return
        blob_client = container_client.get_blob_client(self.raw_file_name)
        if not blob_client.exists():
            log.warning(f'Remote file missing: cannot download {self.raw_file_name}')
            return
        with open(self.local_path, 'wb') as f:
            f.write(blob_client.download_blob().readall())
            log.info(f'{self.local_path} downloaded')

    def read_dataframe(self) -> None:
        """Read raw zstd-compressed file to pandas DataFrame."""
        if not self.local_exists():
            log.warning(f'{self.local_path} missing, cannot read to data frame')
            return
        with open(self.local_path, 'rb') as fh:
            dctx = zstandard.ZstdDecompressor()
            stream_reader = dctx.stream_reader(fh)
            text_stream = io.TextIOWrapper(stream_reader, encoding='utf-8')
            self.dataframe = pandas.read_csv(text_stream)
            
    def filter_dataframe(self, routes: List[str] = None, columns: List[str] = None) -> None:
        """Filter the dataframe, keeping only given columns and rows with given routes.
        With empty params, all columns / all rows are kept, respectively."""
        if self.dataframe is None:
            log.warning('No dataframe read, cannot filter')
            return
        orig_shape = self.dataframe.shape
        if routes is not None:
            self.dataframe = self.dataframe.loc[self.dataframe['route'].isin(routes)]
        if columns is not None:
            self.dataframe = self.dataframe[columns]
        log.info(f'{self.raw_file_name}: {str(orig_shape)} filtered to {str(self.dataframe.shape)}')

    def delete_local(self) -> None:
        if not self.local_exists():
            log.info(f'{self.local_path} missing, cannot delete')
            return
        os.remove(self.local_path)
        log.info(f'{self.local_path} deleted')

class RawHfpDump:
    """Collection of raw HFP messages of multiple types received during given range of hours."""
    
    def __init__(self, 
                 first_datehour: str,
                 last_datehour: str,
                 event_types: List[str]):
        self.first_datehour: datetime = datetime.strptime(first_datehour, '%Y-%m-%dT%H')
        # Upper limit not required, we can fetch one hour only as well.
        if last_datehour is None:
            self.last_datehour = self.first_datehour
        else:
            self.last_datehour: datetime = datetime.strptime(last_datehour, '%Y-%m-%dT%H')
        self.base_name: str = '{0}_{1}'.format(
            self.first_datehour.strftime('%Y-%m-%dT%H'),
            self.last_datehour.strftime('%Y-%m-%dT%H')
        )
        
        self.event_types: List[EventType] = [EventType[evt] for evt in event_types]
        
        self.raw_hfp_files: List[RawHfpFile] = []
        for datehour in datehour_range(self.first_datehour, self.last_datehour):
            for event_type in self.event_types:
                self.raw_hfp_files.append(
                    RawHfpFile(base_name=datehour.strftime('%Y-%m-%dT%H'), 
                               event_type=event_type)
                )
                
        self.container_client: ContainerClient = None
        self.dataframe: pandas.DataFrame = None
        
    def connect_to_container(self) -> None:
        """Connect to remote container."""
        self.container_client = BlobServiceClient.from_connection_string(
            os.getenv('HFP_STORAGE_CONNECTION_STRING')
        ).get_container_client(
                os.getenv('HFP_STORAGE_CONTAINER_NAME')
            )
        
    def download_raw_files(self) -> None:
        """Download compressed csv files by event types to cache."""
        if self.container_client is None:
            self.connect_to_container()
        for rhf in self.raw_hfp_files:
            rhf.download_remote(container_client=self.container_client)
            
    def make_filtered_dataframes(self, routes: List[str], columns: List[str]) -> None:
        """Read raw data files and filter with columns and routes."""
        for rhf in self.raw_hfp_files:
            rhf.read_dataframe()
            rhf.filter_dataframe(routes=routes, columns=columns)
    
    def create_merged_dataframe(self) -> None:
        """Merge dataframes into one, sorted by tsi."""
        self.dataframe = pandas.concat(
            [rhf.dataframe for rhf in self.raw_hfp_files if rhf.dataframe is not None]
        )
        
    def write_to_csv(self) -> None:
        """Write merged dataframe to .csv in cache."""
        if self.dataframe is None:
            log.warning(f'{self.base_name}: dataframe missing, cannot write')
            return
        self.dataframe.to_csv(cached_file_path(f'{self.base_name}.csv'),
                              index=False)
    
    def delete_raw_files(self) -> None:
        """Delete compressed csv files by event types from cache."""
        for rhf in self.raw_hfp_files:
            rhf.delete_local()
    