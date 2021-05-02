SELECT
      urf_code
    , extract(month from date_report) month_report
    , extract(year from date_report) year_report
    , sum(case when posgr = 'МП' then Fact else 0 end) as mp_staff
    , sum(case when posgr = 'Консультант' then Fact else 0 end) as kbp_staff
	, sum(case when posgr = 'РВСП' then Fact else 0 end) as rvsp_staff
	, sum(case when posgr IN ('ЗРВСП', 'ЗРВСПП', 'ЗР ВИП ВСП') then Fact else 0 end) as zrvsp_staff
	, sum(case when posgr  in ('(С)МО', '(С)МО ПФ') then Fact else 0 end) as smo_staff
	, sum(case when posgr  = 'ВМО' then Fact else 0 end) as vmo_staff
    , sum(Fact) as full_staff
FROM   "001_MIS_Retail_Channel".v_rost_SAPHR
where date_report in (
            '2019-01-31',
            '2019-02-28',
            '2019-03-31',
            '2019-04-30',
            '2019-05-31',
            '2019-06-30',
            '2019-07-31',
            '2019-09-30',
            '2019-10-31',
            '2019-12-31',
            '2020-01-31',
            '2020-02-29',
            '2020-03-31',
            '2020-04-30'
)
group by 1, 2, 3
