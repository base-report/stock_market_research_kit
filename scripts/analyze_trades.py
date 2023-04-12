import sqlite3
import csv


summary_query = """
SELECT
  ROUND(
    AVG(
      ((exit_price - entry_price) / entry_price * 100)
    ),
    2
  ) AS avg_gains_pct,
  COUNT(*) AS num_trades
FROM trades;
"""

summary_with_partials_query = """
SELECT
  ROUND(
    AVG(
      CASE
        WHEN partial_target_price IS NOT NULL THEN
          (((partial_target_price * 0.5 + exit_price * 0.5) - entry_price) / entry_price * 100)
        ELSE
          ((exit_price - entry_price) / entry_price * 100)
      END
    ),
    2
  ) AS avg_gains_pct,
  COUNT(*) AS num_trades
FROM trades;
"""

winning_percentages_query = """
WITH gain_categories AS (
  SELECT
    *,
    CASE
      WHEN (exit_price - entry_price) / entry_price >= 0.2 THEN '20%+ Gain'
      WHEN (exit_price - entry_price) / entry_price >= 0.1 THEN '10-20% Gain'
      WHEN (exit_price - entry_price) / entry_price >= 0.05 THEN '5-10% Gain'
      WHEN (exit_price - entry_price) / entry_price >= 0 THEN '0-5% Gain'
      ELSE 'Loss'
    END AS gain_category
  FROM trades
)
SELECT
  gain_category,
  COUNT(*) AS num_trades,
  ROUND(
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM gain_categories)),
    2
  ) AS percentage
FROM gain_categories
WHERE gain_category IN ('Loss', '0-5% Gain', '5-10% Gain', '10-20% Gain', '20%+ Gain')
GROUP BY gain_category
ORDER BY percentage DESC;
"""

winning_percentages_by_sector_query = """
WITH gain_categories AS (
  SELECT
    t.*,
    sd.sector,
    CASE
      WHEN (t.exit_price - t.entry_price) / t.entry_price >= 0.2 THEN '20%+ Gain'
      WHEN (t.exit_price - t.entry_price) / t.entry_price >= 0.1 THEN '10-20% Gain'
      WHEN (t.exit_price - t.entry_price) / t.entry_price >= 0.05 THEN '5-10% Gain'
      WHEN (t.exit_price - t.entry_price) / t.entry_price >= 0 THEN '0-5% Gain'
      ELSE 'Loss'
    END AS gain_category
  FROM trades AS t
  JOIN stock_data AS sd ON t.symbol = sd.symbol
)
SELECT
  gain_category,
  sector,
  COUNT(*) AS num_trades,
  ROUND(
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM gain_categories)),
    2
  ) AS percentage
FROM gain_categories
WHERE gain_category IN ('Loss', '0-5% Gain', '5-10% Gain', '10-20% Gain', '20%+ Gain')
GROUP BY gain_category, sector
ORDER BY gain_category, percentage DESC;
"""

adr_groups_query = """
WITH adr_groups AS (
  SELECT
    *,
    CASE
      WHEN adr20 >= 0.03 AND adr20 < 0.04 THEN '3-4'
      WHEN adr20 >= 0.04 AND adr20 < 0.05 THEN '4-5'
      WHEN adr20 >= 0.05 AND adr20 < 0.06 THEN '5-6'
      WHEN adr20 >= 0.06 AND adr20 < 0.07 THEN '6-7'
      WHEN adr20 >= 0.07 AND adr20 < 0.08 THEN '7-8'
      WHEN adr20 >= 0.08 AND adr20 < 0.10 THEN '8-10'
      WHEN adr20 >= 0.10 AND adr20 < 0.15 THEN '10-15'
      ELSE '16+'
    END AS adr_group
  FROM trades
)
SELECT
  adr_group,
  COUNT(*) AS num_trades,
  ROUND(AVG((exit_price - entry_price) / entry_price * 100), 2) AS avg_gains_pct
FROM adr_groups
GROUP BY adr_group
ORDER BY avg_gains_pct desc;
"""

volume_groups_query = """
WITH volume_groups AS (
  SELECT
    *,
    CASE
      WHEN volume20 >= 100000 AND volume20 < 250000 THEN '100K - 250K'
      WHEN volume20 >= 250000 AND volume20 < 500000 THEN '250K - 500K'
      WHEN volume20 >= 500000 AND volume20 < 1000000 THEN '500K - 1M'
      WHEN volume20 >= 1000000 AND volume20 < 3000000 THEN '1M - 3M'
      ELSE '3M+'
    END AS volume_group
  FROM trades
)
SELECT
  volume_group,
  COUNT(*) AS num_trades,
  ROUND(AVG((exit_price - entry_price) / entry_price * 100), 2) AS avg_gains_pct
FROM volume_groups
GROUP BY volume_group
ORDER BY avg_gains_pct desc;
"""

consolidation_days_groups_query = """
WITH consolidation_days_groups AS (
  SELECT
    *,
    CASE
      WHEN consolidation_days = 5 THEN '5'
      WHEN consolidation_days = 6 THEN '6'
      WHEN consolidation_days = 7 THEN '7'
      WHEN consolidation_days >= 8 AND consolidation_days < 10 THEN '8-9'
      ELSE '10+'
    END AS consolidation_days_group
  FROM trades
)
SELECT
  consolidation_days_group,
  COUNT(*) AS num_trades,
  ROUND(AVG((exit_price - entry_price) / entry_price * 100), 2) AS avg_gains_pct
FROM consolidation_days_groups
GROUP BY consolidation_days_group
ORDER BY avg_gains_pct desc;
"""

year_groups_query = """
SELECT 
  CASE 
    WHEN CAST(strftime('%Y', entry_date) AS INTEGER) <= 1990 THEN '<= 1990'
    ELSE strftime('%Y', entry_date)
  END AS year,
  ROUND(AVG((exit_price - entry_price) / entry_price * 100), 2) AS avg_gains_percent,
  COUNT(*) AS num_trades
FROM trades
GROUP BY year
ORDER BY 
  CASE 
    WHEN year = '<= 1990' THEN 0 
    ELSE 1 
  END,
  year;
"""

month_groups_query = """
SELECT 
  CAST(strftime('%m', entry_date) AS INTEGER) AS month,
  ROUND(AVG((exit_price - entry_price) / entry_price * 100), 2) AS avg_gains_percent,
  COUNT(*) AS num_trades
FROM trades
GROUP BY month
ORDER BY month;
"""

price_groups_query = """
WITH price_groups AS (
  SELECT
    *,
    CASE
      WHEN entry_price < 3 THEN '< $3'
      WHEN entry_price >= 3 AND entry_price < 6 THEN '$3 - $6'
      WHEN entry_price >= 6 AND entry_price < 10 THEN '$6 - $10'
      WHEN entry_price >= 10 AND entry_price < 15 THEN '$10 - $15'
      WHEN entry_price >= 15 AND entry_price < 25 THEN '$15 - $25'
      WHEN entry_price >= 25 AND entry_price < 50 THEN '$25 - $50'
      ELSE '> $50'
    END AS price_group
  FROM trades
)
SELECT
  price_group,
  COUNT(*) AS num_trades,
  ROUND(AVG((exit_price - entry_price) / entry_price * 100), 2) AS avg_gains_pct
FROM price_groups
GROUP BY price_group
ORDER BY avg_gains_pct desc;
"""

# Connect to the database
conn = sqlite3.connect("stock_market_research.db")
cursor = conn.cursor()


def run_query(query):
    cursor.execute(query)
    header = [column[0] for column in cursor.description]
    results = cursor.fetchall()
    return header, results


def save_results_to_csv(header, results, filename):
    full_filename = f"data/csv/{filename}"
    with open(full_filename, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)
        csv_writer.writerows(results)


def analyze_query(query, filename):
    header, results = run_query(query)
    save_results_to_csv(header, results, filename)


def main():
    analyze_query(summary_query, "summary.csv")
    analyze_query(summary_with_partials_query, "summary_with_partials.csv")
    analyze_query(winning_percentages_query, "winning_percentages.csv")
    analyze_query(
        winning_percentages_by_sector_query, "winning_percentages_by_sector.csv"
    )
    analyze_query(adr_groups_query, "adr_groups.csv")
    analyze_query(volume_groups_query, "volume_groups.csv")
    analyze_query(consolidation_days_groups_query, "consolidation_days_groups.csv")
    analyze_query(year_groups_query, "year_groups.csv")
    analyze_query(month_groups_query, "month_groups.csv")
    analyze_query(price_groups_query, "price_groups.csv")

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print("Done!")


if __name__ == "__main__":
    main()
