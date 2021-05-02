SELECT
      urf_code_uni vsp
    , extract(month from date_report) month_report
    , extract(year from date_report) year_report
    , SUM(quantity) sales
    , SUM(case when extract(day from date_report) <= 12 then quantity else 0 end) sales_half
    , max(vl_up) as max_up
    , min(vl_up) as min_up
FROM "001_MIS_RETAIL_REPORTING"."vasm_operations"
WHERE 1=1
        and (PRODUCT_ID = 435 or PRODUCT_ID = 558 or PRODUCT_ID = 557 or PRODUCT_ID = 559 or PRODUCT_ID = 613 or PRODUCT_ID = 635)
        and (OPERATION_ID = 118 or OPERATION_ID = 268)
        and date_report >= date'2018-11-01'
GROUP BY 1, 2, 3