from enum import Enum, auto
from datetime import datetime
from typing import List

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

class RawHfpDump:
    """Collection of raw HFP messages received during the given hour."""
    
    def __init__(self, dump_datetime: datetime, event_types: [str]):
        self.dump_datetime = dump_datetime
        self.event_types = [EventType[evt] for evt in event_types]
        self.base_name = f'{dump_datetime.year}-{dump_datetime.month:02d}-{dump_datetime.day:02d}T{dump_datetime.hour:02d}'