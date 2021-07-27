BEGIN;

CREATE TABLE IF NOT EXISTS public.uf_choices (
	choice_id bigint DEFAULT nextval('choices_seq'::regclass) NOT NULL,
	choice_list character varying NOT NULL,
	"order" integer NOT NULL,
	choice_label character varying NOT NULL,
	"value" character varying NOT NULL,
	programid character varying,
	"language" character varying,
	deploymentnumber integer,
	PRIMARY KEY(choice_id)
);

COMMIT;