CREATE SCHEMA observed;

COMMENT ON SCHEMA observed IS
'Observation data from about realized transit operations, from HFP.';

CREATE TYPE public.pos_event AS enum(
  'VP', 'DUE', 'ARR', 'DEP', 'ARS', 'PDE',
  'PAS', 'WAIT', 'DOO', 'DOC', 'TLR', 'TLA',
  'DA', 'DOUT', 'BA', 'BOUT', 'VJA', 'VJOUT'
);

COMMENT ON TYPE public.pos_event IS
'HFP event types, from
https://digitransit.fi/en/developers/apis/4-realtime-api/vehicle-positions/#event-types';

CREATE TABLE observed.vehicle (
  unique_vehicle_id integer PRIMARY KEY,
  owner_operator_id smallint NOT NULL,
  owner_vehicle_id smallint NOT NULL
);

COMMENT ON TABLE observed.vehicle IS
'Transit vehicles, unique by owner_operator_id and owner_vehicle_id.
Combined under unique_vehicle_id allow single-column vehicle identifiers in other tables.';
COMMENT ON COLUMN observed.vehicle.unique_vehicle_id IS
'Unique vehicle identifier. Should be of format {owner_operator_id * 100000 + owner_vehicle_id}.';
COMMENT ON COLUMN observed.vehicle.owner_operator_id IS
'Id of the operator who owns the vehicle.';
COMMENT ON COLUMN observed.vehicle.owner_vehicle_id IS
'Id of the vehicle, unique by each operator.';

CREATE TABLE observed.monitored_journey (
  monitored_journey_id uuid PRIMARY KEY,
  pattern_id uuid NOT NULL REFERENCES planned.service_pattern(pattern_id),
  operating_date date NOT NULL,
  start_time interval NOT NULL,
  unique_vehicle_id integer NOT NULL REFERENCES observed.vehicle(unique_vehicle_id),
  planned_operator smallint,
  extra_journey_sequence smallint
    CHECK (extra_journey_sequence IS NULL OR extra_journey_sequence >= 2)
);

COMMENT ON TABLE observed.monitored_journey IS
'Real transit service journey driven by a vehicle and recorded in HFP.';
COMMENT ON COLUMN observed.monitored_journey.monitored_journey_id IS
'Unique identifier of the journey. Should be generated from HFP attributes
(route, dir, oday, start, operator_id, vehicle_id) so monitored journeys
are unique by these.';
COMMENT ON COLUMN observed.monitored_journey.pattern_id IS
'Pattern id of the journey (refers to route, direction, and stop pattern).';
COMMENT ON COLUMN observed.monitored_journey.operating_date IS
'Scheduled operating date of the journey.';
COMMENT ON COLUMN observed.monitored_journey.start_time IS
'Scheduled start time of the journey, in 24h clock.';
COMMENT ON COLUMN observed.monitored_journey.unique_vehicle_id IS
'Vehicle that served the journey.';
COMMENT ON COLUMN observed.monitored_journey.planned_operator IS
'Id of the operator the dated journey was assigned to.';
COMMENT ON COLUMN observed.monitored_journey.extra_journey_sequence IS
'Sequence number of the realization of the same dated journey, if realized by multiple vehicles;
if the dated journey was run only once, then NULL.';

CREATE TABLE observed.vehicle_position (
  unique_vehicle_id integer NOT NULL REFERENCES observed.vehicle(unique_vehicle_id),
  pos_timestamp timestamptz NOT NULL,
  monitored_journey_id uuid REFERENCES observed.monitored_journey(monitored_journey_id),
  events public.pos_event[],
  odometer real,
  pos_geom geometry(POINT, 3067) NOT NULL,

  PRIMARY KEY (pos_timestamp, unique_vehicle_id)
);

CREATE INDEX ON observed.vehicle_position USING GIST(pos_geom);

COMMENT ON TABLE observed.vehicle_position IS
'Geographical position and other status values of unique vehicles at each timestamp.';
COMMENT ON COLUMN observed.vehicle_position.unique_vehicle_id IS
'Unique vehicle identifier.';
COMMENT ON COLUMN observed.vehicle_position.pos_timestamp IS
'Timestamp of the HFP message, at full second precision.';
COMMENT ON COLUMN observed.vehicle_position.monitored_journey_id IS
'Id of the journey the vehicle was signed in (if signed).';
COMMENT ON COLUMN observed.vehicle_position.events IS
'ARRAY (!) of event types valid for the given timestamp.
NULL if only "VP" event was emitted.';
COMMENT ON COLUMN observed.vehicle_position.odometer IS
'Odometer value from the vehicle, in meters.';
COMMENT ON COLUMN observed.vehicle_position.pos_geom IS
'Geographical location of the vehicle in ERTS-TM35 coordinates.';

CREATE TABLE observed.door_event (
  unique_vehicle_id integer NOT NULL REFERENCES observed.vehicle(unique_vehicle_id),
  door_open_timestamp timestamptz NOT NULL,
  -- NOTE: DOO->DOC pairs are required, we don't create an event from DOO only.
  door_close_timestamp timestamptz NOT NULL,
  stop_id uuid REFERENCES planned.stop_point(stop_id),
  extra_door_event_sequence smallint
    CHECK (extra_door_event_sequence IS NULL OR extra_door_event_sequence >= 2),
  
  PRIMARY KEY (door_open_timestamp, unique_vehicle_id)
);

COMMENT ON TABLE observed.door_event IS
'Opening any door and closing the last open door of a vehicle creates a door event.
Used for calculating dwell times at stops, for instance.';
COMMENT ON COLUMN observed.door_event.unique_vehicle_id IS
'Unique vehicle identifier.';
COMMENT ON COLUMN observed.door_event.door_open_timestamp IS
'Timestamp when the first door was opened, at full second precision.';
COMMENT ON COLUMN observed.door_event.door_close_timestamp IS
'Timestamp when the last door was closed, at full second precision.';
COMMENT ON COLUMN observed.door_event.stop_id IS
'Unique stop version identifier.
NULL, if the door event occurred outside detected stop areas of the service pattern.';
COMMENT ON COLUMN observed.door_event.extra_door_event_sequence IS
'Sequence number for additional door events during the same stop event.
NULL, if there was only one door event.';

CREATE TABLE observed.stop_event (
  unique_vehicle_id uuid NOT NULL,
  arrival_timestamp timestamptz NOT NULL,
  arrival_obs_type pos_event,
  departure_timestamp timestamptz,
  departure_obs_type pos_event,
  stop_id uuid NOT NULL REFERENCES planned.stop_point(stop_id),
  dwell_time_s real,
  has_driver_change boolean,

  PRIMARY KEY (arrival_timestamp, unique_vehicle_id)
);

COMMENT ON TABLE observed.stop_event IS
'A detected stopping in or passing through a stop area by a transit vehicle.';
COMMENT ON COLUMN observed.stop_event.unique_vehicle_id IS
'Unique vehicle identifier.';
COMMENT ON COLUMN observed.stop_event.arrival_timestamp IS
'Timestamp when the vehicle came to a halt at the stop or entered the stop radius.
See arrival_obs_type.';
COMMENT ON COLUMN observed.stop_event.arrival_obs_type IS
'Which event_type produced arrival_timestamp?';
COMMENT ON COLUMN observed.stop_event.departure_timestamp IS
'Timestamp when the vehicle started from the stop or exited the stop radius.
See departure_obs_type.';
COMMENT ON COLUMN observed.stop_event.departure_obs_type IS
'Which event_type produced departure_timestamp?';
COMMENT ON COLUMN observed.stop_event.stop_id IS
'Unique stop version identifier.';
COMMENT ON COLUMN observed.stop_event.dwell_time_s IS
'Passenger service duration at the stop, i.e., duration of the first
door event during the stop event.';
COMMENT ON COLUMN observed.stop_event.has_driver_change IS
'Did the stop event include a driver change event?';