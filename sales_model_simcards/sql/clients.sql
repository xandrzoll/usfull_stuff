select
      gosb_osb as gosb
    , extract(month from report_date) month_report
    , extract(year from report_date) year_report
    , sum(all_clients) / count(vsp) as avg_clients
from (
        select
              gosb_osb
            , vsp
            , report_date
            , sum(clients_served) as all_clients
        from "001_mis_retail".vfct_sm_suo_operations
        where report_date >= date'2017-12-01'
        group by 1, 2, 3
) as T1
group by 1, 2, 3