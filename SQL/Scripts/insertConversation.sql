SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Dan
-- Create date: 
-- Description:	
-- =============================================
ALTER PROCEDURE insertIntoConversation
	-- Add the parameters for the stored procedure here
	@message VARCHAR(1000) = '',
	@userID VARCHAR(50) = '',
	@isFromUser bit = 1	
AS
BEGIN
	SET NOCOUNT ON;
	
INSERT INTO [dbo].[Conversation]
           ([userID]
           ,[message]
           ,[fromUser]
           ,[isText]
           ,[dateTimeID])
     VALUES
           (@userID
           ,@message
           ,@isFromUser
           ,@isText
           ,GETDATE())

END
GO