from __future__ import annotations

from .db import DATABASE_NAME, ensure_database_exists, mysql_cursor


def initialize_database_and_tables() -> None:
    """
    显式定义表结构并创建：
    - 数据库：x_trading
    - 表：
      1) industry_history_ths（对齐 ak.stock_board_industry_index_ths 常见返回）
      2) stock_history_daily（对齐 get_historical_quotes 返回数据，前复权）
    说明：两表均含唯一键（标识列 + `date`）。
    """
    ensure_database_exists()

    industry_table_sql = """
    CREATE TABLE IF NOT EXISTS `industry_history_ths` (
      `id` BIGINT NOT NULL AUTO_INCREMENT,
      `industry` VARCHAR(255) NOT NULL,
      `日期` DATE NOT NULL,
      `开盘价` FLOAT NULL,
      `收盘价` FLOAT NULL,
      `最高价` FLOAT NULL,
      `最低价` FLOAT NULL,
      `成交量` BIGINT NULL,
      `成交额` FLOAT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uniq_industry_date`(`industry`, `日期`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """

    stock_table_sql = """
    CREATE TABLE IF NOT EXISTS `stock_history_daily` (
      `id` BIGINT NOT NULL AUTO_INCREMENT,
      `code` VARCHAR(16) NOT NULL,
      `date` DATE NOT NULL,
      `open` FLOAT NULL,
      `high` FLOAT NULL,
      `low` FLOAT NULL,
      `close` FLOAT NULL,
      `volume` BIGINT NULL,
      `amount` FLOAT NULL,
      `outstanding_share` BIGINT NULL,
      `turnover` FLOAT NULL,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uniq_code_date`(`code`, `date`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """

    with mysql_cursor(DATABASE_NAME) as cur:
        cur.execute(industry_table_sql)
        cur.execute(stock_table_sql)


