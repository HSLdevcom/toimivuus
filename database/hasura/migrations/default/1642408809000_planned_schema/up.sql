CREATE EXTENSION btree_gist;

CREATE SCHEMA planned;

COMMENT ON SCHEMA planned IS
'Planned transit operations, as seen by vehicles producing HFP data.';

CREATE TABLE planned.stop_point (
  stop_id uuid PRIMARY KEY,
  stop_long_code integer NOT NULL,
  stop_short_code text,
  stop_name text,
  stop_radius_m real,
  hastus_place text,
  stop_geom geometry(POINT, 3067)
);

COMMENT ON TABLE planned.stop_point IS
'Transit stop locations and attributes. A single stop is identified by stop_long_code,
but it can have multiple versions by stop_id, e.g., due to changed location.';
COMMENT ON COLUMN planned.stop_point.stop_id IS
'Unique identifier of the stop *version*.';
COMMENT ON COLUMN planned.stop_point.stop_long_code IS
'Long integer identifier of the stop.';
COMMENT ON COLUMN planned.stop_point.stop_short_code IS
'Short string identifier of the stop. Represents the physical stop or platform:
can be shared by multiple stop_long_codes of different modes (e.g., shared stop for bus and tram).';
COMMENT ON COLUMN planned.stop_point.stop_name IS
'Name of the stop.';
COMMENT ON COLUMN planned.stop_point.stop_radius_m IS
'Effective radius around the stop in meters:
used for triggering HFP stop related events as vehicles enter and exit the radius area.';
COMMENT ON COLUMN planned.stop_point.hastus_place IS
'Optional place id of the stop, marking its use in runtime and schedule planning.';
COMMENT ON COLUMN planned.stop_point.stop_geom IS
'Geographical location of the stop in ERTS-TM35 coordinates.';

CREATE TABLE planned.service_pattern (
  pattern_id uuid PRIMARY KEY,
  route_id text NOT NULL,
  direction_id smallint NOT NULL
    CHECK (direction_id IN (1, 2)),
  valid_between_dates daterange NOT NULL,

  EXCLUDE USING GIST(route_id WITH =, direction_id WITH =, valid_between_dates WITH &&)
);

COMMENT ON TABLE planned.service_pattern IS
'Transit service patterns (ordered stop lists) unique by route, direction,
and range of operation dates. These three attributes are used to match
monitored_journeys to corresponding service patterns.
pattern_id provides a single-column reference to the pattern.';
COMMENT ON COLUMN planned.service_pattern.pattern_id IS
'Unique pattern identifier.';
COMMENT ON COLUMN planned.service_pattern.route_id IS
'Route identifier in the long format, e.g. 1065A.';
COMMENT ON COLUMN planned.service_pattern.direction_id IS
'Direction identifier, either 1 or 2.';
COMMENT ON COLUMN planned.service_pattern.valid_between_dates IS
'Date range during which the pattern is valid. Two patterns of the same route_id and
direction_id must not have overlapping dates.
';

CREATE TABLE planned.stop_point_in_service_pattern (
  pattern_id uuid NOT NULL REFERENCES planned.service_pattern(pattern_id),
  stop_sequence smallint NOT NULL
    CHECK (stop_sequence >= 1),
  stop_id uuid REFERENCES planned.stop_point(stop_id),
  stop_role smallint 
    CHECK (stop_role IS NULL OR stop_role IN (1, 2, 3, 4)),
  -- TODO: Should this be cumulative rather than per-pair distance?
  distance_from_last_stop_m real
    CHECK (distance_from_last_stop_m >= 0.0),

  PRIMARY KEY (pattern_id, stop_sequence)
);

COMMENT ON TABLE planned.stop_point_in_service_pattern IS
'Ordered stop points that form the service pattern of a route and a direction.';
COMMENT ON COLUMN planned.stop_point_in_service_pattern.pattern_id IS
'Unique pattern identifier.';
COMMENT ON COLUMN planned.stop_point_in_service_pattern.stop_sequence IS
'Order number of the stop within the pattern.';
COMMENT ON COLUMN planned.stop_point_in_service_pattern.stop_id IS
'Unique identifier of the stop version visited by the pattern.';
COMMENT ON COLUMN planned.stop_point_in_service_pattern.stop_role IS
'Possible special role of the stop in the pattern: 1 = first stop of the pattern,
2 = regulated (timing) stop, 3 = scheduling stop (active Hastus place), 4 = last stop of the pattern.';
COMMENT ON COLUMN planned.stop_point_in_service_pattern.distance_from_last_stop_m IS
'Planned route path distance to this stop from the last stop in the pattern, in meters.
0 m for the first stop.';
