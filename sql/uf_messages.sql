BEGIN;

CREATE TABLE IF NOT EXISTS public.uf_messages (
	message_uuid character varying NOT NULL,
	programid character varying NOT NULL,
	deploymentnumber integer NOT NULL,
	recipientid character varying NOT NULL,
	talkingbookid character varying NOT NULL,
	deployment_tbcdid character varying,
	deployment_timestamp timestamp without time zone NOT NULL,
	deployment_user character varying,
	test_deployment boolean,
	collection_tbcdid character varying,
	collection_timestamp timestamp without time zone NOT NULL,
	collection_user character varying,
	length_seconds integer NOT NULL,
	length_bytes integer NOT NULL,
	"language" character varying NOT NULL,
	date_recorded date,
	relation character varying,
	bundle_uuid character varying,
	PRIMARY KEY(message_uuid)
);

COMMIT;