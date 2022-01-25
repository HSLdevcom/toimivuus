import logging as log
import os
import requests
import urllib.parse
from enum import Enum, auto
from datetime import datetime
from typing import List

def remote_file_path(fname: str):
    """Append fname to STORAGE_URL_ROOT."""
    url = os.getenv('STORAGE_URL_ROOT')
    return urllib.parse.urljoin(url, fname)

def cached_file_path(fname: str):
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
    """Points to a file of raw HFP messages of single type received an hour."""

    REQUEST_TIMEOUT_S=2

    def __init__(self, base_name: str, event_type: EventType):
        self.raw_file_name = f'{base_name}_{event_type.name}.csv.zst'
        self.remote_path = remote_file_path(self.raw_file_name)
        self.local_path = cached_file_path(self.raw_file_name)
    
    def remote_exists(self):
        try:
            r = requests.head(self.remote_path, timeout=self.REQUEST_TIMEOUT_S)
            return r.status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    def local_exists(self):
        return os.path.exists(self.local_path)

class RawHfpDump:
    """Collection of raw HFP messages of multiple types received during given hour."""
    
    def __init__(self, dump_datetime: datetime, event_types: [str]):
        self.dump_datetime = dump_datetime
        self.event_types = [EventType[evt] for evt in event_types]
        self.base_name = f'{dump_datetime.year}-{dump_datetime.month:02d}-{dump_datetime.day:02d}T{dump_datetime.hour:02d}'