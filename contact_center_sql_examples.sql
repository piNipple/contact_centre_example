/*
Учебный SQL-проект: анализ эффективности контакт-центра.
Данные синтетические. Проект демонстрирует GROUP BY, CASE WHEN,
CTE, JOIN и оконную функцию.

СУБД: PostgreSQL
*/

-- 1. Общие показатели по операторам
SELECT
    agent_id,
    COUNT(*) AS contacts,
    ROUND(AVG(call_duration_min), 2) AS avg_call_duration_min,
    ROUND(AVG(wait_time_min), 2) AS avg_wait_time_min,
    ROUND(AVG(customer_rating), 2) AS avg_rating,
    SUM(sale) AS sales,
    ROUND(100.0 * AVG(resolved), 2) AS resolution_rate_pct
FROM contacts
GROUP BY agent_id
ORDER BY sales DESC;


-- 2. Конверсия в продажу по типу обращения
SELECT
    issue_type,
    COUNT(*) AS contacts,
    SUM(sale) AS sales,
    ROUND(100.0 * AVG(sale), 2) AS conversion_pct
FROM contacts
GROUP BY issue_type
ORDER BY conversion_pct DESC;


-- 3. Сравнение регионов
SELECT
    region,
    COUNT(*) AS contacts,
    ROUND(AVG(wait_time_min), 2) AS avg_wait_min,
    ROUND(AVG(call_duration_min), 2) AS avg_duration_min,
    ROUND(100.0 * AVG(resolved), 2) AS resolution_rate_pct
FROM contacts
GROUP BY region
ORDER BY avg_wait_min DESC;


-- 4. Найти операторов с количеством продаж выше среднего
WITH agent_sales AS (
    SELECT
        agent_id,
        SUM(sale) AS sales
    FROM contacts
    GROUP BY agent_id
),
avg_sales AS (
    SELECT AVG(sales) AS mean_sales
    FROM agent_sales
)
SELECT
    a.agent_id,
    a.sales
FROM agent_sales a
CROSS JOIN avg_sales s
WHERE a.sales > s.mean_sales
ORDER BY a.sales DESC;


-- 5. Ранжирование операторов по количеству продаж
WITH agent_metrics AS (
    SELECT
        agent_id,
        COUNT(*) AS contacts,
        SUM(sale) AS sales,
        ROUND(100.0 * AVG(sale), 2) AS conversion_pct
    FROM contacts
    GROUP BY agent_id
)
SELECT
    agent_id,
    contacts,
    sales,
    conversion_pct,
    DENSE_RANK() OVER (ORDER BY sales DESC) AS sales_rank
FROM agent_metrics
ORDER BY sales_rank;
