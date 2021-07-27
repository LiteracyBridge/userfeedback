BEGIN;

CREATE TABLE IF NOT EXISTS public.uf_questions (
	id bigint DEFAULT nextval('questions_seq'::regclass) NOT NULL,
	name character varying NOT NULL,
	"order" integer NOT NULL,
	"type" character varying NOT NULL,
	question_label character varying NOT NULL,
	"data" character varying NOT NULL,
	data_other character varying,
	required boolean DEFAULT false NOT NULL,
	"constraint" character varying,
	relevant character varying,
	choice_list character varying,
	programid character varying,
	"language" character varying,
	deploymentnumber integer,
	"default" character varying,
	hint character varying,
	PRIMARY KEY(id)
);

COMMIT;