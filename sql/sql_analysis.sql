-- =============================================================================
-- STEP 3: SQL ANALYSIS — RETAIL BUSINESS INTELLIGENCE
-- =============================================================================
-- Author : [Your Name]
-- Dataset: Superstore (cleaned)
-- Engine : Compatible with PostgreSQL / MySQL / SQLite
-- Purpose: Revenue, profit, trends, regional performance, and growth analysis
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- SETUP: Create and load the table (adjust for your DB engine)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS superstore (
    Row_ID           INT PRIMARY KEY,
    Order_ID         VARCHAR(20),
    Order_Date       DATE,
    Ship_Date        DATE,
    Ship_Mode        VARCHAR(20),
    Customer_ID      VARCHAR(10),
    Customer_Name    VARCHAR(100),
    Segment          VARCHAR(20),
    Country          VARCHAR(50),
    City             VARCHAR(50),
    State            VARCHAR(50),
    Postal_Code      VARCHAR(10),
    Region           VARCHAR(10),
    Product_ID       VARCHAR(20),
    Category         VARCHAR(20),
    Sub_Category     VARCHAR(20),
    Product_Name     VARCHAR(200),
    Sales            DECIMAL(10,2),
    Quantity         INT,
    Discount         DECIMAL(5,2),
    Profit           DECIMAL(10,2),
    Shipping_Days    INT,
    Revenue          DECIMAL(10,2),
    Profit_Margin    DECIMAL(8,2),
    Cost             DECIMAL(10,2),
    Has_Discount     INT,
    Order_Year       INT,
    Order_Month      INT,
    Order_Quarter    INT,
    Order_DayOfWeek  VARCHAR(15),
    Order_YearMonth  VARCHAR(10),
    Order_Size       VARCHAR(10),
    Profit_Category  VARCHAR(15)
);


-- =============================================================================
-- QUERY 1: EXECUTIVE SUMMARY — Total Revenue, Profit, Orders, Avg Order Value
-- =============================================================================

SELECT
    COUNT(DISTINCT Order_ID)                        AS Total_Orders,
    COUNT(DISTINCT Customer_ID)                     AS Total_Customers,
    ROUND(SUM(Sales), 2)                            AS Total_Revenue,
    ROUND(SUM(Profit), 2)                           AS Total_Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2)  AS Overall_Profit_Margin_Pct,
    ROUND(SUM(Sales) / COUNT(DISTINCT Order_ID), 2) AS Avg_Order_Value,
    ROUND(AVG(Discount) * 100, 2)                   AS Avg_Discount_Pct
FROM superstore;


-- =============================================================================
-- QUERY 2: MONTHLY SALES TREND — Time-Series Revenue & Profit
-- =============================================================================

SELECT
    Order_YearMonth,
    COUNT(DISTINCT Order_ID)   AS Orders,
    ROUND(SUM(Sales), 2)       AS Monthly_Revenue,
    ROUND(SUM(Profit), 2)      AS Monthly_Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS Profit_Margin_Pct
FROM superstore
GROUP BY Order_YearMonth
ORDER BY Order_YearMonth;


-- =============================================================================
-- QUERY 3: YEAR-OVER-YEAR (YoY) GROWTH — Using Window Functions
-- =============================================================================

WITH yearly_metrics AS (
    SELECT
        Order_Year,
        ROUND(SUM(Sales), 2)   AS Annual_Revenue,
        ROUND(SUM(Profit), 2)  AS Annual_Profit,
        COUNT(DISTINCT Order_ID) AS Total_Orders
    FROM superstore
    GROUP BY Order_Year
)
SELECT
    Order_Year,
    Annual_Revenue,
    Annual_Profit,
    Total_Orders,
    LAG(Annual_Revenue) OVER (ORDER BY Order_Year) AS Prev_Year_Revenue,
    ROUND(
        (Annual_Revenue - LAG(Annual_Revenue) OVER (ORDER BY Order_Year))
        / NULLIF(LAG(Annual_Revenue) OVER (ORDER BY Order_Year), 0) * 100, 2
    ) AS Revenue_Growth_YoY_Pct,
    ROUND(
        (Annual_Profit - LAG(Annual_Profit) OVER (ORDER BY Order_Year))
        / NULLIF(LAG(Annual_Profit) OVER (ORDER BY Order_Year), 0) * 100, 2
    ) AS Profit_Growth_YoY_Pct
FROM yearly_metrics
ORDER BY Order_Year;


-- =============================================================================
-- QUERY 4: REGION-WISE PERFORMANCE
-- =============================================================================

SELECT
    Region,
    COUNT(DISTINCT Order_ID)                        AS Orders,
    COUNT(DISTINCT Customer_ID)                     AS Customers,
    ROUND(SUM(Sales), 2)                            AS Revenue,
    ROUND(SUM(Profit), 2)                           AS Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS Profit_Margin_Pct,
    ROUND(AVG(Discount) * 100, 2)                   AS Avg_Discount_Pct,
    RANK() OVER (ORDER BY SUM(Sales) DESC)          AS Revenue_Rank
FROM superstore
GROUP BY Region
ORDER BY Revenue DESC;


-- =============================================================================
-- QUERY 5: STATE-LEVEL DEEP DIVE — Top 10 & Bottom 10 States by Profit
-- =============================================================================

-- Top 10 most profitable states
SELECT
    State,
    ROUND(SUM(Sales), 2)    AS Revenue,
    ROUND(SUM(Profit), 2)   AS Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS Profit_Margin_Pct,
    COUNT(DISTINCT Order_ID) AS Orders
FROM superstore
GROUP BY State
ORDER BY Profit DESC
LIMIT 10;

-- Bottom 10 loss-making states (revenue leakage!)
SELECT
    State,
    ROUND(SUM(Sales), 2)    AS Revenue,
    ROUND(SUM(Profit), 2)   AS Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS Profit_Margin_Pct,
    ROUND(AVG(Discount) * 100, 2) AS Avg_Discount_Pct
FROM superstore
GROUP BY State
ORDER BY Profit ASC
LIMIT 10;


-- =============================================================================
-- QUERY 6: TOP PRODUCTS & CATEGORIES
-- =============================================================================

-- 6a. Category-Level Performance
SELECT
    Category,
    COUNT(DISTINCT Product_ID)  AS Products,
    COUNT(DISTINCT Order_ID)    AS Orders,
    ROUND(SUM(Sales), 2)        AS Revenue,
    ROUND(SUM(Profit), 2)       AS Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS Profit_Margin_Pct
FROM superstore
GROUP BY Category
ORDER BY Revenue DESC;

-- 6b. Sub-Category Performance with Ranking
SELECT
    Category,
    Sub_Category,
    ROUND(SUM(Sales), 2)      AS Revenue,
    ROUND(SUM(Profit), 2)     AS Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS Profit_Margin_Pct,
    RANK() OVER (PARTITION BY Category ORDER BY SUM(Sales) DESC) AS Rank_In_Category
FROM superstore
GROUP BY Category, Sub_Category
ORDER BY Category, Revenue DESC;

-- 6c. Top 10 Products by Revenue
SELECT
    Product_Name,
    Category,
    Sub_Category,
    ROUND(SUM(Sales), 2)   AS Revenue,
    ROUND(SUM(Profit), 2)  AS Profit,
    SUM(Quantity)           AS Units_Sold
FROM superstore
GROUP BY Product_Name, Category, Sub_Category
ORDER BY Revenue DESC
LIMIT 10;


-- =============================================================================
-- QUERY 7: DISCOUNT VS PROFIT ANALYSIS — Revenue Leakage Detection
-- =============================================================================

-- 7a. Impact of discount levels on profitability
SELECT
    CASE
        WHEN Discount = 0      THEN 'No Discount'
        WHEN Discount <= 0.1   THEN '1–10%'
        WHEN Discount <= 0.2   THEN '11–20%'
        WHEN Discount <= 0.3   THEN '21–30%'
        WHEN Discount <= 0.4   THEN '31–40%'
        ELSE '40%+'
    END AS Discount_Bucket,
    COUNT(*) AS Transactions,
    ROUND(SUM(Sales), 2)   AS Revenue,
    ROUND(SUM(Profit), 2)  AS Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS Profit_Margin_Pct,
    ROUND(AVG(Profit), 2)  AS Avg_Profit_Per_Item
FROM superstore
GROUP BY Discount_Bucket
ORDER BY Discount_Bucket;

-- 7b. Discounted vs Non-Discounted comparison
SELECT
    CASE WHEN Has_Discount = 1 THEN 'Discounted' ELSE 'Full Price' END AS Pricing,
    COUNT(*) AS Transactions,
    ROUND(SUM(Sales), 2)   AS Revenue,
    ROUND(SUM(Profit), 2)  AS Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS Profit_Margin_Pct,
    ROUND(
        SUM(Sales) * 100.0 / SUM(SUM(Sales)) OVER (), 2
    ) AS Revenue_Share_Pct
FROM superstore
GROUP BY Has_Discount;


-- =============================================================================
-- QUERY 8: CUSTOMER SEGMENT ANALYSIS
-- =============================================================================

SELECT
    Segment,
    COUNT(DISTINCT Customer_ID)   AS Customers,
    COUNT(DISTINCT Order_ID)      AS Orders,
    ROUND(SUM(Sales), 2)          AS Revenue,
    ROUND(SUM(Profit), 2)         AS Profit,
    ROUND(AVG(Sales), 2)          AS Avg_Order_Value,
    ROUND(SUM(Sales) / COUNT(DISTINCT Customer_ID), 2) AS Revenue_Per_Customer
FROM superstore
GROUP BY Segment
ORDER BY Revenue DESC;


-- =============================================================================
-- QUERY 9: SHIPPING ANALYSIS
-- =============================================================================

SELECT
    Ship_Mode,
    COUNT(*) AS Transactions,
    ROUND(AVG(Shipping_Days), 1) AS Avg_Ship_Days,
    ROUND(SUM(Sales), 2)         AS Revenue,
    ROUND(SUM(Profit), 2)        AS Profit,
    ROUND(SUM(Profit) / NULLIF(SUM(Sales), 0) * 100, 2) AS Profit_Margin_Pct
FROM superstore
GROUP BY Ship_Mode
ORDER BY Revenue DESC;


-- =============================================================================
-- QUERY 10: QUARTERLY HEATMAP DATA — Region × Quarter Performance
-- =============================================================================

SELECT
    Region,
    Order_Quarter,
    Order_Year,
    ROUND(SUM(Sales), 2)   AS Revenue,
    ROUND(SUM(Profit), 2)  AS Profit,
    COUNT(DISTINCT Order_ID) AS Orders
FROM superstore
GROUP BY Region, Order_Quarter, Order_Year
ORDER BY Order_Year, Order_Quarter, Region;


-- =============================================================================
-- QUERY 11: CUMULATIVE REVENUE — Running Total with Window Functions
-- =============================================================================

SELECT
    Order_YearMonth,
    ROUND(SUM(Sales), 2) AS Monthly_Revenue,
    ROUND(
        SUM(SUM(Sales)) OVER (ORDER BY Order_YearMonth), 2
    ) AS Cumulative_Revenue,
    ROUND(
        SUM(SUM(Profit)) OVER (ORDER BY Order_YearMonth), 2
    ) AS Cumulative_Profit
FROM superstore
GROUP BY Order_YearMonth
ORDER BY Order_YearMonth;


-- =============================================================================
-- QUERY 12: LOSS-MAKING ORDERS — Revenue Leakage Investigation
-- =============================================================================

SELECT
    Order_ID,
    Customer_Name,
    Segment,
    Region,
    Category,
    Sub_Category,
    ROUND(Sales, 2)    AS Revenue,
    ROUND(Profit, 2)   AS Profit,
    Discount,
    ROUND(Profit_Margin, 2) AS Profit_Margin_Pct
FROM superstore
WHERE Profit < 0
ORDER BY Profit ASC
LIMIT 20;


-- =============================================================================
-- QUERY 13: MOVING AVERAGES — 3-Month Rolling Revenue
-- =============================================================================

WITH monthly AS (
    SELECT
        Order_YearMonth,
        ROUND(SUM(Sales), 2) AS Revenue
    FROM superstore
    GROUP BY Order_YearMonth
)
SELECT
    Order_YearMonth,
    Revenue,
    ROUND(AVG(Revenue) OVER (
        ORDER BY Order_YearMonth
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS Rolling_3M_Avg
FROM monthly
ORDER BY Order_YearMonth;
