
SET DATEFIRST 1;
With Attendence as (
	SELECT
		Date
		,DATEADD(dd, -( DAY( Date ) -1 ), Date) as SOMonth
		,DATENAME(WEEKDAY,Date) as DayName
		,DATEPART(dw,Date) as DayNumber
		,DATEPART(month,Date) as MonthNumber
		,DATEPART(wk, Date) as WeekNumber
		,100*DATEPART(year, Date)+  DATEPART(wk, Date) as YearWeek
		,SUM(Desks_Booked) as Desks_Booked
		,SUM(Desks_Used) as Desks_Used
		,SUM([Directorate_Numbers]) as TotalStaff
		,(1.0*SUM(Desks_Used)/SUM([Directorate_Numbers])) as PctOnSite
	FROM Bronze.AccessByDirectorate
	GROUP BY Date
	HAVING SUM(Desks_Used) is not null
), DailyMeetings as (
	SELECT
		Date
		,SUM(Attendance) as Total_Attendees
		,COUNT(*) as Total_Meetings

	FROM [Bronze].[Meetings]
	GROUP BY Date


), Retail as (
	SELECT
		Date
		,SUM(a.Daily_Transactions) as Daily_Transactions
		,SUM(a.Breakfast) as Breakfast
		,SUM(a.Lunch) as Lunch
		,SUM(a.Hot_Meals) as Hot_Meals

	FROM [Bronze].[RestaurantConversions] a 
	WHERE [Site/Location] <> 'Sandyford'
	GROUP BY Date 

), WDPMonth as (
	SELECT SOMonth, COUNT(*) as WDPMonth
	FROM Attendence
	GROUP BY SOMonth

), DailyWaste as (
	SELECT 
		a.Month as SOMonth
		--,b.WDPMonth
		,a.Biodegradable as MonthlyBDW -- Biodegradable Waste
		,a.MMW as MonthlyMMW -- Mixed Municipal Waste
		,a.MDR as MonthlyMDR -- Mixed dry recycling
		,a.Total as TotalMonthlyWaste
	FROM [Bronze].[Waste] a
	--JOIN WDPMonth b on a.Month=b.SOMonth
	WHERE a.Site='Docklands'
)

SELECT
	a.Date

	-- Addition time dimensions
	-- ,a.DayName as Day_Name
	-- ,a.DayNumber as Day_Number
	-- ,a.WeekNumber as Week_Number
	-- ,a.MonthNumber as Month_Number
	-- ,a.YearWeek as Year_And_Week

	-- leading variables, known ahead of time
	,a.Desks_Booked
	,a.TotalStaff as Total_Staff
	,b.mintp as Min_Air_Temp
	,b.maxtp as Max_Air_Temp
	,b.rain as Rainfall
	,b.wdsp as Windspeed
	,COALESCE(c.Primary_Holiday,0) as School_Holiday
	,j.Annual_Leave
	,j.Flexi_Leave
	,j.Total_Leave
	,r.WDPMonth as Work_Days_Per_Month
	,d.Total_Attendees
	,d.Total_Meetings

	-- Lagged variables - potential labels
	,e.FTE as FTE_Count
	,f.Space_Usage as Car_Parking_Occupancy
	,f.Capacity as Car_Parking_Capacity
	,g.Space_Usage as Motorbike_Parking_Occupancy
	,g.Capacity as Motorbike_Parking_Capacity
	,h.Space_Usage as Bike_Parking_Occupancy
	,h.Capacity as Bike_Parking_Capacity
	,i.Daily_Transactions
	,i.Breakfast
	,i.Lunch
	,i.Hot_Meals
	,k.Remote_access_VPN_Max_Concurrent_Usage as VPN_cnxn
	,k.Webex_Connections as Meeting_Cnxns
	,k.Webex_Total_Participants as Meeting_Participants
	,k.Webex_Maximum_Concurrent_Meetings as Concurrent_Meetings
	,k.[Average_Meeting_Duration_Times_(Minutes)] as Meeting_Duration
	,ko.Remote_access_VPN_Max_Concurrent_Usage as VPN_cnxn_ori
	,ko.Webex_Connections as Meeting_Cnxns_ori
	,ko.Webex_Total_Participants as Meeting_Participants_ori
	,ko.Webex_Maximum_Concurrent_Meetings as Concurrent_Meetings_ori
	,ko.[Average_Meeting_Duration_Times_(Minutes)] as Meeting_Duration_ori
	,l.[PRIVA_Electricity_Consumption_(kWh)] as Total_Electric_KWh
	,l.[Day_Time_8:00_to_23:00_NWQ] as Day_Electric_KWh
	,lo.[Day_Time_8:00_to_23:00_NWQ] as Day_Electric_KWh_ori
	,l.[Night_Time_23:00_to_8:00_NWQ] as Night_Electric_KWh
	,lo.[Night_Time_23:00_to_8:00_NWQ] as Night_Electric_KWh_ori
	,m.[NWQ_Gas_Consumption_(m³)] as Gas_Consumption
	,m.Kitchen_Usage
	,m.NWQ_Air_Con_ticket as Air_Conditioning
	--,m.Mean_Temputaure as Mean_Temperature_Gas_Data
	,n.[Water_consumption_(m³)] as Water_Consumption
	,no.[Water_consumption_(m³)] as Water_Consumption_ori
	,o.Cold_Consumption
	,oo.Cold_Consumption as Cold_Consumption_ori
	,o.Heat_Consumption
	,oo.Heat_Consumption as Heat_Consumption_ori
	--,o.Mean_Temp as Mean_Temperature_Cold_Heat
	,p.MonthlyBDW as Total_Monthly_Biodegradable
	,p.MonthlyMMW as Total_Monthly_Landfill
	,p.MonthlyMDR as Total_Monthly_Recycable
	,p.TotalMonthlyWaste as Total_Monthly_Waste
	,q.East as East_Floor_Usage
	,q.West as West_Floor_Usage



	-- Label fields:
	,a.Desks_Used as Actual_Desks_Used
	-- ,a.PctOnSite as Pct_On_Site

	

FROM Attendence a
LEFT JOIN [Bronze].[DailyWeather] b on a.Date = b.date
LEFT JOIN [Bronze].[HolidayCalendar] c on a.Date = c.date 
LEFT JOIN DailyMeetings d on a.Date = d.Date
LEFT JOIN [Bronze].NWQAccess e on a.Date = e.Date
LEFT JOIN [Bronze].[Parking] f on a.Date = f.Date and f.Vechile = 'Car' and f.Site = 'NWQ' and f.ParkingID not in (629,633) -- sandyford parking mislabeled
LEFT JOIN [Bronze].[Parking] g on a.Date = g.Date and g.Vechile = 'Motorbike' and g.Site = 'NWQ'
LEFT JOIN [Bronze].[Parking] h on a.Date = h.Date and h.Vechile = 'Bike' and h.Site = 'NWQ'
LEFT JOIN Retail i on a.Date = i.Date
LEFT JOIN [Bronze].[StaffLeave] j on a.Date = j.Date
LEFT JOIN [Bronze].[VPNUsage] k on a.Date = k.Dates
LEFT JOIN [Bronze].[VPNUsage_original] ko on a.Date = ko.Dates
LEFT JOIN [Bronze].[ElectrictyUsage] l on a.Date = l.Date
LEFT JOIN [Bronze].[ElectrictyUsage_original] lo on a.Date = lo.Date
LEFT JOIN [Bronze].[GasUsage] m on a.Date = m.Date
LEFT JOIN [Bronze].[WaterUsage] n on a.Date = n.Date
LEFT JOIN [Bronze].[WaterUsage_original] no on a.Date = no.Date
LEFT JOIN [Bronze].[ColdAndHeat] o on a.Date = o.Date
LEFT JOIN [Bronze].[ColdAndHeat_original] oo on a.Date = oo.Date
LEFT JOIN DailyWaste p on a.SOMonth=p.SOMonth
LEFT JOIN [Bronze].[FloorUsageEastWest] q on a.Date = q.Date
LEFT JOIN WDPMonth r on a.SOMonth = r.SOMonth



WHERE c.Public_Holiday is null

ORDER BY 1 ASC


