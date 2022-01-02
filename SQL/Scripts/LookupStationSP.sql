SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Dan
-- Create date: 31/12/21
-- Description:	
-- =============================================
Alter PROCEDURE LookupStation 
	@searchTerm varchar(50) = ''
AS
BEGIN
	SET NOCOUNT ON;
	
	IF (SELECT count(*)
		  FROM [AIChatBot].[dbo].[Stations]
		  where name LIKE '%' + @searchTerm + '%' 
			  or longname_name_alias LIKE '%' + @searchTerm + '%' 
			  or alpha3 LIKE '%' + @searchTerm + '%'
			  or tiploc LIKE '%' + @searchTerm + '%'
			  or column5 LIKE '%' + @searchTerm + '%') > 0
		SELECT *
		  FROM [AIChatBot].[dbo].[Stations]
		  where name LIKE '%' + @searchTerm + '%' 
			  or longname_name_alias LIKE '%' + @searchTerm + '%' 
			  or alpha3 LIKE '%' + @searchTerm + '%'
			  or tiploc LIKE '%' + @searchTerm + '%'
			  or column5 LIKE '%' + @searchTerm + '%'
	ELSE
		DECLARE @pos INT = 2 -- location where we want first space 
		WHILE @pos < LEN(@searchTerm)+1 
			BEGIN 
				SET @searchTerm = STUFF(@searchTerm, @pos, 0, ']%['); 
				SET @pos = @pos+4; 
			END 

		SELECT *
		  FROM [AIChatBot].[dbo].[Stations]
		  where name LIKE '%[' + @searchTerm + ']%' 	  
		  or alpha3 LIKE '%[' + @searchTerm + ']%'
		  or tiploc LIKE '%[' + @searchTerm + ']%'
		  or column5 LIKE '%[' + @searchTerm + ']%'
END
GO
