SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Dan
-- Create date: 
-- Description:	
-- =============================================
CREATE PROCEDURE GetLatenessOfBoth
	-- Add the parameters for the stored procedure here
	@FROM varchar(7) = '', 
	@TO varchar(7) = ''
AS
BEGIN
	SET NOCOUNT ON;

	WITH RAW_CTE as (
	SELECT *,
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
	and (tpl = @FROM or tpl = @TO))

SELECT (CASE
		WHEN c1.arr IS NOT NULL AND c1.dep IS NULL THEN c1.arr
		WHEN c1.arr IS NULL AND c1.dep IS NOT NULL THEN c1.dep
		WHEN c1.arr IS NOT NULL AND c1.dep IS NOT NULL THEN (c1.arr + c1.dep)/2
	END) as fromLateBy,
	(CASE
		WHEN c2.arr IS NOT NULL AND c2.dep IS NULL THEN c2.arr
		WHEN c2.arr IS NULL AND c2.dep IS NOT NULL THEN c2.dep
		WHEN c2.arr IS NOT NULL AND c2.dep IS NOT NULL THEN (c2.arr + c2.dep)/2
	END) as toLateBy
FROM RAW_CTE c1
JOIN RAW_CTE c2 ON c1.rid = c2.rid
WHERE c1.tpl = @FROM and c2.tpl = @TO
END
GO