WITH CTE AS (SELECT ROW_NUMBER() OVER(PARTITION BY rid ORDER BY (CASE 
	WHEN pta IS NOT NULL THEN pta 
	WHEN ptd IS NOT NULL AND pta IS NULL THEN ptd 
	WHEN arr_at IS NOT NULL AND ptd IS NULL AND pta IS NULL THEN arr_at
	ELSE dep_at END) ASC) 
    AS Row#,
rid,tpl
FROM nrch_livst_a51
where pta is not null or ptd is not null or arr_at is not null or dep_at is not null)
SELECT tpl,count(Distinct Row#) from CTE group by tpl