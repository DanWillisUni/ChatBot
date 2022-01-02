SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Dan
-- Create date: 
-- Description:	
-- =============================================
ALTER PROCEDURE GetLateness 
	-- Add the parameters for the stored procedure here
	@pta varchar(5) = NULL, 
	@arr_at varchar(5) = NULL,
	@ptd varchar(5) = NULL, 
	@dep_at varchar(5) = NULL
AS
BEGIN
	SET NOCOUNT ON;

	WITH RAW_CTE as (
		SELECT 
			(CASE
				WHEN @pta IS NOT NULL and @arr_at IS NOT NULL and (SUBSTRING(@pta,0,3)='23' or SUBSTRING(@pta,0,3)='22' or SUBSTRING(@pta,0,3)='21') and DATEDIFF(MINUTE,@pta,@arr_at) <-1000 THEN 1440+DATEDIFF(MINUTE,@pta,@arr_at)
				WHEN @pta IS NOT NULL and @arr_at IS NOT NULL and SUBSTRING(@pta,0,3)='00' and DATEDIFF(MINUTE,@pta,@arr_at) >1000 THEN -1440+DATEDIFF(MINUTE,@pta,@arr_at)
				WHEN @pta IS NOT NULL and @arr_at IS NOT NULL THEN DATEDIFF(MINUTE,@pta,@arr_at)
				ELSE NULL
			END) as arr,
			(CASE
				WHEN @ptd IS NOT NULL and @dep_at IS NOT NULL and (SUBSTRING(@ptd,0,3)='23' or SUBSTRING(@ptd,0,3)='22' or SUBSTRING(@ptd,0,3)='21') and DATEDIFF(MINUTE,@ptd,@dep_at) <-1000 THEN 1440+DATEDIFF(MINUTE,@ptd,@dep_at)
				WHEN @ptd IS NOT NULL and @dep_at IS NOT NULL and SUBSTRING(@ptd,0,3)='00' and DATEDIFF(MINUTE,@ptd,@dep_at) >1000 THEN -1440+DATEDIFF(MINUTE,@ptd,@dep_at)
				WHEN @ptd IS NOT NULL and @dep_at IS NOT NULL THEN DATEDIFF(MINUTE,@ptd,@dep_at)
				ELSE NULL
			END) as dep		
	)

SELECT 
	(CASE
		WHEN arr IS NOT NULL AND dep IS NULL THEN arr
		WHEN arr IS NULL AND dep IS NOT NULL THEN dep
		WHEN arr IS NOT NULL AND dep IS NOT NULL THEN (arr + dep)/2
		ELSE NULL
	END)
FROM RAW_CTE

END
GO