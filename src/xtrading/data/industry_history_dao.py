from __future__ import annotations

from typing import Any, List, Optional, Tuple

import pandas as pd

from .db import DATABASE_NAME, mysql_cursor


TABLE_NAME = "industry_history_ths"
ID_COL = "id"
IDENTITY_COL = "industry"  # 标识行业名称


class IndustryHistoryDAO:
    def upsert_dataframe(self, industry: str, df: pd.DataFrame) -> int:
        """将 ak.stock_board_industry_index_ths 返回的 DataFrame 写入/更新到表中。
        约定：为该 DataFrame 每行写入额外列 `industry` 作为唯一键的一部分。
        返回：受影响的行数。
        """
        if df.empty:
            return 0
        df = df.copy()
        # 标准化日期列：支持索引为日期或列名为“日期”
        if '日期' not in df.columns:
            if isinstance(df.index, pd.DatetimeIndex) or str(df.index.name) in ('date', '日期', '交易日期', 'time', '时间'):
                df = df.reset_index()
                if 'index' in df.columns:
                    df = df.rename(columns={'index': '日期'})
        # 仅保留显式定义列（与 get_board_industry_hist 返回一致）
        target_cols = ['industry', '日期', '开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额']
        df[IDENTITY_COL] = industry
        for col in target_cols:
            if col not in df.columns:
                df[col] = None
        df = df[target_cols]

        placeholders = ", ".join(["%s"] * len(target_cols))
        col_list = ", ".join([f"`{c}`" for c in target_cols])
        update_list = ", ".join([f"`{c}`=VALUES(`{c}`)" for c in target_cols if c not in (ID_COL, IDENTIFY_COL := IDENTITY_COL, '日期')])
        sql = (
            f"INSERT INTO `{TABLE_NAME}` ({col_list}) VALUES ({placeholders}) "
            f"ON DUPLICATE KEY UPDATE {update_list}"
        )

        values: List[Tuple[Any, ...]] = [tuple(row[c] for c in target_cols) for _, row in df.iterrows()]
        affected = 0
        with mysql_cursor(DATABASE_NAME) as cur:
            affected += cur.executemany(sql, values)
        return affected

    def query_by_industry(self, industry: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        where = ["`industry`=%s"]
        params: List[Any] = [industry]
        # 常见日期列名，择一命中
        date_candidates = ["日期", "date", "交易日期", "time", "时间"]
        date_col_sql = None
        with mysql_cursor(DATABASE_NAME) as cur:
            # 找一列日期列
            cur.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}`;")
            cols = [r["Field"] for r in cur.fetchall()]
            for dc in date_candidates:
                if dc in cols:
                    date_col_sql = f"`{dc}`"
                    break

        if start_date and date_col_sql:
            where.append(f"{date_col_sql} >= %s")
            params.append(start_date)
        if end_date and date_col_sql:
            where.append(f"{date_col_sql} <= %s")
            params.append(end_date)

        where_sql = " AND ".join(where)
        sql = f"SELECT * FROM `{TABLE_NAME}` WHERE {where_sql} ORDER BY {date_col_sql or ID_COL} ASC;"
        with mysql_cursor(DATABASE_NAME) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return pd.DataFrame(rows)

    def query_by_industries(self, industries: List[str], start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """批量查询多个板块的历史数据"""
        if not industries:
            return pd.DataFrame()
        
        where = [f"`industry` IN ({', '.join(['%s'] * len(industries))})"]
        params: List[Any] = list(industries)
        # 常见日期列名，择一命中
        date_candidates = ["日期", "date", "交易日期", "time", "时间"]
        date_col_sql = None
        with mysql_cursor(DATABASE_NAME) as cur:
            # 找一列日期列
            cur.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}`;")
            cols = [r["Field"] for r in cur.fetchall()]
            for dc in date_candidates:
                if dc in cols:
                    date_col_sql = f"`{dc}`"
                    break

        if start_date and date_col_sql:
            where.append(f"{date_col_sql} >= %s")
            params.append(start_date)
        if end_date and date_col_sql:
            where.append(f"{date_col_sql} <= %s")
            params.append(end_date)

        where_sql = " AND ".join(where)
        sql = f"SELECT * FROM `{TABLE_NAME}` WHERE {where_sql} ORDER BY `industry`, {date_col_sql or ID_COL} ASC;"
        with mysql_cursor(DATABASE_NAME) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return pd.DataFrame(rows)

    def delete_by_industry(self, industry: str) -> int:
        with mysql_cursor(DATABASE_NAME) as cur:
            return cur.execute(f"DELETE FROM `{TABLE_NAME}` WHERE `{IDENTITY_COL}`=%s;", (industry,))


