DECLARE @FromStation varchar(7) = 'SOTON', 
	@ToStation varchar(7) = 'WATRLMN';

WITH RAW_CTE as (
		SELECT rid,tpl,
			(CASE
				WHEN pta IS NOT NULL and arr_at IS NOT NULL and (SUBSTRING(pta,0,3)='23' or SUBSTRING(pta,0,3)='22' or SUBSTRING(pta,0,3)='21') and DATEDIFF(MINUTE,pta,arr_at) <-1000 THEN 1440+DATEDIFF(MINUTE,pta,arr_at)
				WHEN pta IS NOT NULL and arr_at IS NOT NULL and SUBSTRING(pta,0,3)='00' and DATEDIFF(MINUTE,pta,arr_at) >1000 THEN -1440+DATEDIFF(MINUTE,pta,arr_at)
				WHEN pta IS NOT NULL and arr_at IS NOT NULL THEN DATEDIFF(MINUTE,pta,arr_at)
				ELSE NULL
			END) as arr,
			(CASE
				WHEN ptd IS NOT NULL and dep_at IS NOT NULL and (SUBSTRING(ptd,0,3)='23' or SUBSTRING(ptd,0,3)='22' or SUBSTRING(ptd,0,3)='21') and DATEDIFF(MINUTE,ptd,dep_at) <-1000 THEN 1440+DATEDIFF(MINUTE,ptd,dep_at)
				WHEN ptd IS NOT NULL and dep_at IS NOT NULL and SUBSTRING(ptd,0,3)='00' and DATEDIFF(MINUTE,ptd,dep_at) >1000 THEN -1440+DATEDIFF(MINUTE,ptd,dep_at)
				WHEN ptd IS NOT NULL and dep_at IS NOT NULL THEN DATEDIFF(MINUTE,ptd,dep_at)
				ELSE NULL
			END) as dep
		FROM [nrch_livst_a51]
		where ((pta IS NOT NULL and arr_at IS NOT NULL)OR(ptd IS NOT NULL and dep_at IS NOT NULL))
		and (tpl = @FromStation or tpl = @ToStation)
	)
,allData AS (
SELECT x.rid,tpl,
	(CASE
		WHEN arr IS NOT NULL AND dep IS NULL THEN arr
		WHEN arr IS NULL AND dep IS NOT NULL THEN dep
		WHEN arr IS NOT NULL AND dep IS NOT NULL THEN (arr + dep)/2
	END) as lateBy
FROM RAW_CTE
INNER JOIN (SELECT rid FROM RAW_CTE
	GROUP BY rid
	HAVING COUNT(*) > 1) x ON x.rid = RAW_CTE.rid
)

SELECT TOP(100) c1.lateBy as fromLateBy,c2.lateBy as toLateBy
FROM allData c1
JOIN allData c2 ON c1.rid = c2.rid
WHERE c1.tpl = @FromStation and c2.tpl = @ToStation