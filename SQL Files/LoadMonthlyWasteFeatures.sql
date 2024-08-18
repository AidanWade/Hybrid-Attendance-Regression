
SELECT --[Date]
      --,DATEADD(dd, -( DAY( Date ) -1 ), Date) as SOMonth
      EOMONTH(Date,1) as EOMonth
      ,1.0*[Total_Monthly_Biodegradable]/[Work_Days_Per_Month] as Avg_Biogradable_lastmonth
      ,1.0*[Total_Monthly_Landfill]/[Work_Days_Per_Month] as Avg_Landfill_lastmonth
      ,1.0*[Total_Monthly_Recycable]/[Work_Days_Per_Month] as Avg_Recyclable_lastmonth
      ,1.0*[Total_Monthly_Waste]/[Work_Days_Per_Month] as Avg_Total_Waste_lastmonth
FROM [Silver].[All_Raw_Features]
WHERE Work_Days_Per_Month > 15
GROUP BY EOMONTH(Date,1),[Total_Monthly_Biodegradable],[Total_Monthly_Landfill],[Total_Monthly_Recycable],[Total_Monthly_Waste],[Work_Days_Per_Month]
