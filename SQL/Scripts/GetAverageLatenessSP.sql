SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Dan
-- Create date: 
-- Description:	
-- =============================================
ALTER PROCEDURE GetAverageLateness 
	-- Add the parameters for the stored procedure here
	@FromStation varchar(7) = '', 
	@ToStation varchar(7) = '',
	@LateBy INT = 0
AS
BEGIN
	SET NOCOUNT ON;
	SELECT AVG(DATEDIFF(MINUTE,pta,arr_at)) 
	FROM [nrch_livst_a51] 
	where tpl = @ToStation
		and rid in (SELECT rid
		FROM [nrch_livst_a51] 
		WHERE tpl = @FromStation 
			and DATEDIFF(MINUTE,pta,arr_at) = @LateBy)
END
GO
