SET DATEFIRST 1;

SELECT [Date]
      --,EOMONTH(Date) as EOMonth
      ,[Desks_Booked]
      ,[Total_Staff]
      ,[Min_Air_Temp]
      ,[Max_Air_Temp]
      ,[Rainfall]
      ,[Windspeed]
      ,[School_Holiday]
      ,[Annual_Leave]
      ,[Flexi_Leave]
      ,[Total_Leave]
      ,[Work_Days_Per_Month]
      ,[Total_Attendees]
      ,[Total_Meetings]
      ,[FTE_Count]
      ,[Car_Parking_Occupancy]
      ,[Car_Parking_Capacity]
      ,[Motorbike_Parking_Occupancy]
      ,[Motorbike_Parking_Capacity]
      ,[Bike_Parking_Occupancy]
      ,[Bike_Parking_Capacity]
      ,[Daily_Transactions]
      ,[Breakfast]
      ,[Lunch]
      ,[Hot_Meals]
      ,[VPN_cnxn]
      --,[Webex_Connections]
      --,[Webex_Total_Participants]
      --,[Webex_Maximum_Concurrent_Meetings]
	  ,Meeting_Cnxns
      ,Meeting_Participants
	  ,Concurrent_Meetings
	  ,Meeting_Duration
      ,[VPN_cnxn_ori]
      --,[Webex_Connections_ori]
      --,[Webex_Total_Participants_ori]
      --,[Webex_Maximum_Concurrent_Meetings_ori]
	  ,Meeting_Cnxns_ori
      ,Meeting_Participants_ori
	  ,Concurrent_Meetings_ori
	  ,Meeting_Duration_ori
      ,[Total_Electric_KWh]
      ,[Day_Electric_KWh]
      ,[Day_Electric_KWh_ori]
      ,[Night_Electric_KWh]
      ,[Night_Electric_KWh_ori]
      ,[Gas_Consumption]
      ,[Kitchen_Usage]
      ,[Air_Conditioning]
      ,[Water_Consumption]
      ,[Water_Consumption_ori]
      ,[Cold_Consumption]
      ,[Heat_Consumption]
      ,[Cold_Consumption_ori]
      ,[Heat_Consumption_ori]
      ,[East_Floor_Usage]
      ,[West_Floor_Usage]

      ,DATEPART(dw,Date) as Day_Of_Week
	--   ,DATEPART(month,Date) as Month
      ,DATEPART(q,Date) as Quarter
	  --,DATEPART(wk, Date) as Week_Number
      ,[Actual_Desks_Used]
      --,[Day]
      --,[Pct_On_Site]
      --,[Week_Number]
      --,[Year]
  FROM [Silver].[All_Raw_Features]
  ORDER BY 1