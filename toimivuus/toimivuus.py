import logging as log
import os
import requests
import urllib.parse
from azure.storage.blob import ContainerClient
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
    
    def __init__(self, dump_datetime: datetime, event_types: List[str]):
        self.dump_datetime = dump_datetime
        self.event_types = [EventType[evt] for evt in event_types]
        self.base_name = f'{dump_datetime.year}-{dump_datetime.month:02d}-{dump_datetime.day:02d}T{dump_datetime.hour:02d}'