SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Dan
-- Create date: 
-- Description:	
-- =============================================
ALTER PROCEDURE CompareStations
	-- Add the parameters for the stored procedure here
	@A VARCHAR(7) = '',
	@B VARCHAR(7) = ''
AS
BEGIN
	SET NOCOUNT ON;

	WITH CTE as (SELECT TOP(1000) rid,tpl,
	(CASE 
		WHEN pta IS NOT NULL THEN pta 
		WHEN ptd IS NOT NULL AND pta IS NULL THEN ptd 
		WHEN arr_at IS NOT NULL AND ptd IS NULL AND pta IS NULL THEN arr_at
		ELSE dep_at END) as time
FROM nrch_livst_a51
where 
	rid in (
		SELECT c1.rid 
		FROM nrch_livst_a51 c1
		INNER JOIN nrch_livst_a51 c2 on c1.rid = c2.rid 
		where c1.tpl = @A
		and c2.tpl = @B
		and (CASE 
			WHEN c1.pta IS NOT NULL THEN c1.pta 
			WHEN c1.ptd IS NOT NULL AND c1.pta IS NULL THEN c1.ptd 
			WHEN c1.arr_at IS NOT NULL AND c1.ptd IS NULL AND c1.pta IS NULL THEN c1.arr_at
			ELSE c1.dep_at END) IS NOT NULL
		and (CASE 
			WHEN c2.pta IS NOT NULL THEN c2.pta 
			WHEN c2.ptd IS NOT NULL AND c2.pta IS NULL THEN c2.ptd 
			WHEN c2.arr_at IS NOT NULL AND c2.ptd IS NULL AND c2.pta IS NULL THEN c2.arr_at
			ELSE c2.dep_at END) IS NOT NULL
		)
	and (tpl = @A or tpl = @B))
	
SELECT AVG(DATEDIFF(MINUTE,c1.time,c2.time)) FROM CTE c1
INNER JOIN CTE c2 on c1.rid = c2.rid 
	where c1.tpl = @A
	and c2.tpl = @B
END
GO