BEGIN;

CREATE SCHEMA IF NOT EXISTS philosophy;

CREATE TABLE IF NOT EXISTS "philosophy"."cyberleninka" (
	"id" uuid NOT NULL,
	"text_id" uuid NOT NULL,
	"tittle" TEXT NOT NULL,
	"magazine_name" TEXT,
	"keywords" TEXT,
	"filed_of_science" TEXT,
	"annotation" TEXT,
	"en_annotation" TEXT,
	"source_url" TEXT,
	"pdf_url" TEXT,
	"publication_year" int8,
	"date_add" timestamptz NOT NULL,
	"date_update" timestamptz NOT NULL,
	CONSTRAINT "philosophy.cyberleninka_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."authors" (
	"id" uuid NOT NULL,
	"name" TEXT NOT NULL,
	"description" TEXT,
	"date_add" timestamptz NOT NULL,
	"date_update" timestamptz NOT NULL,
	CONSTRAINT "philosophy.authors_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."article_text" (
	"id" uuid NOT NULL,
	"text" TEXT NOT NULL,
	"date_add" timestamptz NOT NULL,
	"date_update" timestamptz NOT NULL,
	CONSTRAINT "philosophy.article_text_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."tags" (
	"id" uuid NOT NULL,
	"name" character [200] NOT NULL,
	"date_add" timestamptz NOT NULL,
	"date_update" timestamptz NOT NULL,
	CONSTRAINT "philosophy.tags_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."philosophy_ru" (
	"id" uuid NOT NULL UNIQUE,
	"tittle" TEXT NOT NULL,
	"publication_year" int NOT NULL,
	"publishing_house" TEXT,
	"category" TEXT,
	"url_pdf" TEXT,
	"source_url" TEXT NOT NULL,
	"for_citation" TEXT,
	"source" TEXT NOT NULL,
	"annotation" TEXT,
	"about" TEXT,
	"date_add" timestamptz NOT NULL,
	"date_update" timestamptz NOT NULL,
	CONSTRAINT "philosophy.philosophy_ru_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."gtmarket" (
	"id" uuid NOT NULL,
	"tittle" TEXT NOT NULL UNIQUE,
	"nomination" TEXT,
	"text_id" uuid NOT NULL,
	"source_url" TEXT NOT NULL,
	"definition" TEXT,
	"date_publish" date NOT NULL,
	"date_add" timestamptz NOT NULL,
	"date_update" timestamptz NOT NULL,
	CONSTRAINT "philosophy.gtmarket_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."authors_articles" (
	"id" uuid NOT NULL,
	"author_id" uuid NOT NULL,
	"article_id" uuid NOT NULL,
	"date_add" timestamptz NOT NULL,
	"date_update" timestamptz NOT NULL,
	CONSTRAINT "philosophy.authors_articles_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."tags_article" (
	"id" uuid NOT NULL,
	"tag_name" character [200] NOT NULL,
	"id_tag" uuid NOT NULL,
	"article_id" uuid NOT NULL,
	"date_add" timestamptz NOT NULL,
	"date_update" timestamptz NOT NULL,
	CONSTRAINT "philosophy.tags_article_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."major_article_info" (
	"id" uuid NOT NULL,
	"title" TEXT NOT NULL UNIQUE,
	"source_url" TEXT NOT NULL UNIQUE,
	CONSTRAINT "philosophy.major_article_info_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."magazines" (
	"id" uuid NOT NULL,
	"descriptions" TEXT NOT NULL,
	"url" TEXT NOT NULL,
	"date_add" TIME NOT NULL,
	"date_update" TIME NOT NULL,
	CONSTRAINT "philosophy.magazines_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."magazines_article" (
	"id" uuid NOT NULL unique,
	"tittle" TEXT NOT NULL,
	"magazine_name" TEXT NOT NULL,
	"magazine_issues_name" TEXT NOT NULL,
	"annotation" TEXT NOT NULL,
	"citation" TEXT,
	"source_url" TEXT NOT NULL,
	"pdf_url" TEXT NOT NULL,
	"magazine_id" uuid NOT NULL,
	"magazine_issues_id" uuid NOT NULL,
	"text_id" uuid NOT NULL,
	"date_add" TIME NOT NULL,
	"date_update" TIME NOT NULL,
	CONSTRAINT "philosophy.magazines_article_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE IF NOT EXISTS "philosophy"."magazine_issues" (
	"id" uuid NOT NULL,
	"id_magazine" uuid NOT NULL,
	"release_date" TIME NOT NULL,
	"source_url" TEXT NOT NULL,
	"date_add" TIME NOT NULL,
	"date_update" TIME NOT NULL,
	CONSTRAINT "philosophy.magazine_issues_pk" PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



ALTER TABLE "philosophy"."cyberleninka" ADD CONSTRAINT "cyberleninka_fk0"
    FOREIGN KEY ("id") REFERENCES "philosophy"."major_article_info"("id");
ALTER TABLE "philosophy"."cyberleninka" ADD CONSTRAINT "cyberleninka_fk1"
    FOREIGN KEY ("text_id") REFERENCES "philosophy"."article_text"("id");


ALTER TABLE "philosophy"."philosophy_ru" ADD CONSTRAINT "philosophy_ru_fk0"
    FOREIGN KEY ("id") REFERENCES "philosophy"."major_article_info"("id");

ALTER TABLE "philosophy"."gtmarket" ADD CONSTRAINT "gtmarket_fk0"
    FOREIGN KEY ("id") REFERENCES "philosophy"."major_article_info"("id");
ALTER TABLE "philosophy"."gtmarket" ADD CONSTRAINT "gtmarket_fk1"
    FOREIGN KEY ("text_id") REFERENCES "philosophy"."article_text"("id");

ALTER TABLE "philosophy"."authors_articles" ADD CONSTRAINT "authors_articles_fk0"
    FOREIGN KEY ("author_id") REFERENCES "philosophy"."authors"("id");
ALTER TABLE "philosophy"."authors_articles" ADD CONSTRAINT "authors_articles_fk1"
    FOREIGN KEY ("article_id") REFERENCES "philosophy"."major_article_info"("id");

ALTER TABLE "philosophy"."tags_article" ADD CONSTRAINT "tags_article_fk0"
    FOREIGN KEY ("id_tag") REFERENCES "philosophy"."tags"("id");
ALTER TABLE "philosophy"."tags_article" ADD CONSTRAINT "tags_article_fk1"
    FOREIGN KEY ("article_id") REFERENCES "philosophy"."major_article_info"("id");

ALTER TABLE "philosophy"."magazines_article" ADD CONSTRAINT "magazines_article_fk0"
    FOREIGN KEY ("id") REFERENCES "philosophy"."major_article_info"("id");
ALTER TABLE "philosophy"."magazines_article" ADD CONSTRAINT "magazines_article_fk1"
    FOREIGN KEY ("magazine_id") REFERENCES "philosophy"."magazines"("id");
ALTER TABLE "philosophy"."magazines_article" ADD CONSTRAINT "magazines_articles_fk2"
    FOREIGN KEY ("magazine_issues_id") REFERENCES "philosophy"."magazine_issues"("id");
ALTER TABLE "philosophy"."magazines_article" ADD CONSTRAINT "magazines_article_fk3"
    FOREIGN KEY ("text_id") REFERENCES "philosophy"."article_text"("id");

ALTER TABLE "philosophy"."magazine_issues" ADD CONSTRAINT "magazine_issues_fk0"
    FOREIGN KEY ("id_magazine") REFERENCES "philosophy"."magazines"("id");

COMMIT;
