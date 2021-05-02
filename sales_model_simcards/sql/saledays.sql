SELECT
      vsp
    , extract(month from date_report) month_report
    , extract(year from date_report) year_report
    , sum(case when EMPLOYEE_POSITION = 'МЕНЕДЖЕР ПО ПРОДАЖАМ' then 1 else 0 end) as workdays_mp
    , sum(case when EMPLOYEE_POSITION = 'КОНСУЛЬТАНТ' then 1 else 0 end) as workdays_kbp
FROM (
    SELECT
          urf_code_uni vsp
        , date_report
        , EMPLOYEE_POSITION
        , EMPLOYEE_ID
    FROM "001_MIS_RETAIL_REPORTING"."vasm_operations"
    WHERE 1=1
        and date_report >= date'2018-11-01'
        and EMPLOYEE_POSITION in ('КОНСУЛЬТАНТ', 'МЕНЕДЖЕР ПО ПРОДАЖАМ')
    group by 1, 2, 3, 4
) as T1
group by 1, 2, 3