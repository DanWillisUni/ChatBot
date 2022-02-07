SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:		Dan
-- Create date: 
-- Description:	
-- =============================================
CREATE PROCEDURE insertIntoConversation
	-- Add the parameters for the stored procedure here
	@message VARCHAR(1000) = '',
	@userID VARCHAR(50) = '',
	@isFromUser bit = 1	
AS
BEGIN
	SET NOCOUNT ON;
	
	INSERT INTO [AIChatBot].[dbo].[Conversation_Record]
           ([userID]
           ,[message]
           ,[fromUser]
           ,[dateTimeID])
     VALUES
           (@userID
           ,(CASE 
				WHEN @message = '' THEN null
				ELSE @message
			END)
           ,@isFromUser
           ,GETDATE());
	SELECT 0
END
GO