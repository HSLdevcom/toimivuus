CREATE SCHEMA data_import;

COMMENT ON SCHEMA data_import IS
'Staging tables, views, and procedures for importing 
and transforming data into the database
(extract, load, transform).';

CREATE TABLE data_import.compact_hfp (
  tsi integer NOT NULL,
  operator_id smallint NOT NULL,
  veh smallint NOT NULL,
  route text,
  dir smallint,
  oday date,
  start interval,
  oper smallint,
  events public.pos_event[],
  odo real,
  drst boolean,
  stop integer,
  long double precision,
  lat double precision,

  PRIMARY KEY (tsi, operator_id, veh)
);

COMMENT ON TABLE data_import.compact_hfp IS
'HFP messages merged by (tsi, operator_id, veh).
Describe location and status of a vehicle at the given integer second.
Original event types are composed into events array,
except VP is left out as it is a default event type for every second.';

COMMENT ON COLUMN data_import.compact_hfp.tsi IS
'Unix time in integer seconds from the vehicle.';
COMMENT ON COLUMN data_import.compact_hfp.operator_id IS
'Unique id of the operator who owns the vehicle.';
COMMENT ON COLUMN data_import.compact_hfp.veh IS
'Vehicle number visible on the vehicle, unique within owner.';
COMMENT ON COLUMN data_import.compact_hfp.route IS
'Route id of the trip the vehicle is signed in to.';
COMMENT ON COLUMN data_import.compact_hfp.dir IS
'Direction id of the trip the vehicle is signed in to.';
COMMENT ON COLUMN data_import.compact_hfp.oday IS
'Operating day of the trip the vehicle is signed in to.';
COMMENT ON COLUMN data_import.compact_hfp.start IS
'Scheduled first stop departure time of the trip the vehicle is signed in to.
Follows 24-hour clock (unlike GTFS), 
although the interval type supports times over 24:00:00.';
COMMENT ON COLUMN data_import.compact_hfp.oper IS
'Unique id of the operator running the trip the vehicle is signed in to.
Can differ from operator_id, e.g., due to subcontracted service.';
COMMENT ON COLUMN data_import.compact_hfp.events IS
'Event types (except VP) effective for that vehicle and second combined into an array.
NULL, if only VP event was sent.';
COMMENT ON COLUMN data_import.compact_hfp.odo IS
'Odometer reading (in meters) from the vehicle, independent from the GPS location.
Values are not quite reliable, they jump in steps of several meters, can be negative,
and can reset to zero even in the middle of a trip.';
COMMENT ON COLUMN data_import.compact_hfp.drst IS
'Door status of the vehicle.
TRUE if any door is open, FALSE if all doors are closed.';
COMMENT ON COLUMN data_import.compact_hfp.stop IS
'Integer id (stop_long_code) of the transit stop the vehicle is serving.
Based on detection within the radius of a stop belonging to the trip
the vehicle is signed in to.
NULL if the vehicle is not within a stop area.';
COMMENT ON COLUMN data_import.compact_hfp.long IS
'Vehicle GPS WGS84 longitude in degrees.';
COMMENT ON COLUMN data_import.compact_hfp.lat IS
'Vehicle GPS WGS84 latitude in degrees.';