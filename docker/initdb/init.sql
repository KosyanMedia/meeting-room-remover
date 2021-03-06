-- Table: public.calendar_events

-- DROP TABLE public.calendar_events;

CREATE TABLE IF NOT EXISTS public.calendar_events
(
    id bigserial,
    event_id character varying,
    event_start timestamp without time zone,
    event_end timestamp  without time zone,
    event_creator character varying,
    event_location character varying,
    event_location_name character varying,
    CONSTRAINT calendar_events_event_id_key UNIQUE (event_id)
);

ALTER TABLE public.calendar_events
    OWNER to docker;


-- Table: public.slack_logins

-- DROP TABLE public.slack_logins;

CREATE TABLE IF NOT EXISTS public.slack_logins
(
	id bigserial
		constraint slack_logins_pk
			primary key,
	user_id character varying not null,
	username character varying,
	ip character varying,
	office character varying,
	last_date timestamp,
	email character varying,
	user_tz character varying,
	pdate date not null
);

create unique index slack_logins_user_id_pdate_uindex
	on public.slack_logins (user_id, pdate);

ALTER TABLE public.slack_logins
    OWNER to docker;
