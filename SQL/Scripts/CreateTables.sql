USE [AIChatBot]
GO
/****** Object:  Table [dbo].[Stations]    Script Date: 23/12/2021 18:49:53 ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Stations]') AND type in (N'U'))
DROP TABLE [dbo].[Stations]
GO
/****** Object:  Table [dbo].[nrch_livst_a51]    Script Date: 23/12/2021 18:49:53 ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[nrch_livst_a51]') AND type in (N'U'))
DROP TABLE [dbo].[nrch_livst_a51]
GO
/****** Object:  Table [dbo].[nrch_livst_a51]    Script Date: 23/12/2021 18:49:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[nrch_livst_a51](
	[rid] [char](16) NULL,
	[tpl] [char](7) NULL,
	[pta] [char](5) NULL,
	[ptd] [char](5) NULL,
	[wta] [char](8) NULL,
	[wtp] [char](8) NULL,
	[wtd] [char](8) NULL,
	[arr_et] [char](5) NULL,
	[arr_wet] [char](5) NULL,
	[arr_atremoved] [bit] NULL,
	[pass_et] [char](5) NULL,
	[pass_wet] [char](5) NULL,
	[pass_atremoved] [bit] NULL,
	[dep_et] [char](5) NULL,
	[dep_wet] [char](5) NULL,
	[dep_atremoved] [bit] NULL,
	[arr_at] [char](5) NULL,
	[pass_at] [char](5) NULL,
	[dep_at] [char](5) NULL,
	[cr_code] [smallint] NULL,
	[lr_code] [smallint] NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Stations]    Script Date: 23/12/2021 18:49:53 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Stations](
	[name] [nvarchar](50) NOT NULL,
	[longname_name_alias] [nvarchar](50) NULL,
	[alpha3] [nvarchar](50) NULL,
	[tiploc] [nvarchar](50) NOT NULL,
	[column5] [nvarchar](50) NULL
) ON [PRIMARY]
GO
