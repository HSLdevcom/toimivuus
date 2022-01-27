import logging as log
import os
from azure.storage.blob import BlobServiceClient, ContainerClient
from enum import Enum, auto
from datetime import datetime
from typing import List

def cached_file_path(fname: str) -> str:
    """Append fname to DATA_CACHE_DIRECTORY."""
    cache = os.getenv('DATA_CACHE_DIRECTORY')
    return os.path.join(cache, fname)

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

    def __init__(self, base_name: str, event_type: EventType, container_client: ContainerClient=None):
        self.raw_file_name = f'{base_name}_{event_type.name}.csv.zst'
        self.local_path = cached_file_path(self.raw_file_name)
        if container_client is not None:
            self.blob_client = container_client.get_blob_client(self.raw_file_name)
        else:
            self.blob_client = None
        self.data = None
    
    def remote_exists(self) -> bool:
        return self.blob_client is not None and self.blob_client.exists()

    def local_exists(self) -> bool:
        return os.path.exists(self.local_path)

    def download_remote(self) -> None:
        if not self.remote_exists():
            log.warning(f'Remote file missing: cannot download {self.raw_file_name}')
            return
        with open(self.local_path, 'wb') as f:
            f.write(self.blob_client.download_blob().readall())
            log.info(f'{self.local_path} downloaded')

    def delete_local(self) -> None:
        if not self.local_exists():
            log.info(f'{self.local_path} missing, cannot delete')
            return
        os.remove(self.local_path)
        log.info(f'{self.local_path} deleted')

class RawHfpDump:
    """Collection of raw HFP messages of multiple types received during given hour."""
    
    def __init__(self, 
                 dump_date_hour: str, 
                 event_types: List[str], ):
        dump_datetime: datetime = datetime.strptime(dump_date_hour,
                                                    '%Y-%m-%dT%H')
        self.event_types: List[EventType] = [EventType[evt] for evt in event_types]
        self.base_name: str = f'{dump_datetime.year}-{dump_datetime.month:02d}-{dump_datetime.day:02d}T{dump_datetime.hour:02d}'
        container_client = BlobServiceClient.from_connection_string(os.getenv('HFP_STORAGE_CONNECTION_STRING')).get_container_client(os.getenv('HFP_STORAGE_CONTAINER_NAME'))
        self.raw_hfp_files: List[RawHfpFile] = [RawHfpFile(base_name=self.base_name, event_type=evt, container_client=container_client) for evt in self.event_types]
        
    def download_raw_files(self) -> None:
        """Download compressed csv files by event types to cache."""
        for rhf in self.raw_hfp_files:
            rhf.download_remote()
    
    def create_merged_file(self, columns: List[str], routes: List[str]) -> None:
        """Merge csv files by event type into one file that contains
        the specified columns and rows with specified routes only."""
        pass
    
    def delete_raw_files(self) -> None:
        """Delete compressed csv files by event types from cache."""
        for rhf in self.raw_hfp_files:
            rhf.delete_local()
    
    