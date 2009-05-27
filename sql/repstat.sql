CREATE VIEW "better_represent_repstat_max_stat" AS
SELECT "better_represent_repstat"."stat", "better_represent_repstat"."rep_id", COUNT("better_represent_repstat"."id") AS "num_stats" FROM "better_represent_repstat" GROUP BY "better_represent_repstat"."stat", "better_represent_repstat"."rep_id";

