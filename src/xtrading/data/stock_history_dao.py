from __future__ import annotations

from typing import Any, List, Optional, Tuple

import pandas as pd

from .db import DATABASE_NAME, mysql_cursor


TABLE_NAME = "stock_history_daily"
ID_COL = "id"
IDENTITY_COL = "code"  # 股票代码


class StockHistoryDAO:
    def upsert_dataframe(self, code: str, df: pd.DataFrame) -> int:
        """将 get_historical_quotes 返回的 DataFrame 写入/更新到表中。
        约定：为该 DataFrame 每行写入额外列 `code` 作为唯一键的一部分。
        返回数据字段：date, open, high, low, close, volume, amount, outstanding_share, turnover
        返回：受影响的行数。
        """
        if df.empty:
            return 0
        df = df.copy()
        
        # 标准化日期列（先处理 index，再处理列名）
        if 'date' not in df.columns:
            if isinstance(df.index, pd.DatetimeIndex) or str(df.index.name) in ('date', '日期', '交易日期', 'time', '时间'):
                df = df.reset_index()
                # 重置index后，日期列可能在 'index' 或其他列中
                for col in ['index', 'date', '日期', '交易日期']:
                    if col in df.columns:
                        df = df.rename(columns={col: 'date'})
                        break
        
        # 目标列：与接口返回数据列名保持一致（英文列名）
        target_cols = ['code', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'outstanding_share', 'turnover']
        
        df[IDENTITY_COL] = code
        
        # 确保所有目标列存在
        for col in target_cols:
            if col not in df.columns:
                df[col] = None
        
        # 只选择目标列
        df = df[target_cols]

        placeholders = ", ".join(["%s"] * len(target_cols))
        col_list = ", ".join([f"`{c}`" for c in target_cols])
        update_list = ", ".join([f"`{c}`=VALUES(`{c}`)" for c in target_cols if c not in (ID_COL, IDENT_COL := IDENTITY_COL, 'date')])
        sql = (
            f"INSERT INTO `{TABLE_NAME}` ({col_list}) VALUES ({placeholders}) "
            f"ON DUPLICATE KEY UPDATE {update_list}"
        )

        values: List[Tuple[Any, ...]] = [tuple(row[c] for c in target_cols) for _, row in df.iterrows()]
        with mysql_cursor(DATABASE_NAME) as cur:
            affected = cur.executemany(sql, values)
        return affected

    def query_by_code(self, code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        where = ["`code`=%s"]
        params: List[Any] = [code]
        # 使用英文列名 date
        date_col_sql = "`date`"

        if start_date:
            where.append(f"{date_col_sql} >= %s")
            params.append(start_date)
        if end_date:
            where.append(f"{date_col_sql} <= %s")
            params.append(end_date)

        where_sql = " AND ".join(where)
        sql = f"SELECT * FROM `{TABLE_NAME}` WHERE {where_sql} ORDER BY {date_col_sql} ASC;"
        with mysql_cursor(DATABASE_NAME) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return pd.DataFrame(rows)

    def query_by_codes(self, codes: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """批量查询多个股票代码的历史数据"""
        if not codes:
            return pd.DataFrame()
        
        where = [f"`code` IN ({', '.join(['%s'] * len(codes))})"]
        params: List[Any] = list(codes)
        # 使用英文列名 date
        date_col_sql = "`date`"

        if start_date:
            where.append(f"{date_col_sql} >= %s")
            params.append(start_date)
        if end_date:
            where.append(f"{date_col_sql} <= %s")
            params.append(end_date)

        where_sql = " AND ".join(where)
        sql = f"SELECT * FROM `{TABLE_NAME}` WHERE {where_sql} ORDER BY `code`, {date_col_sql} ASC;"
        with mysql_cursor(DATABASE_NAME) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return pd.DataFrame(rows)

    def delete_by_code(self, code: str) -> int:
        with mysql_cursor(DATABASE_NAME) as cur:
            return cur.execute(f"DELETE FROM `{TABLE_NAME}` WHERE `{IDENTITY_COL}`=%s;", (code,))


