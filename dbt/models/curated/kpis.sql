
-- kpis.sql
SELECT
    warehouse,
    AVG(quantity) as avg_quantity,
    COUNT(DISTINCT order_id) as total_orders
FROM {{ ref('stg_orders') }}
GROUP BY warehouse