from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from xtrading.repositories.stock.industry_info_query import IndustryInfoQuery
from xtrading.repositories.stock.stock_query import StockQuery
from xtrading.static.industry_sectors import INDUSTRY_SECTORS

from .industry_history_dao import IndustryHistoryDAO
from .stock_history_dao import StockHistoryDAO


def _yyyymmdd(date: datetime) -> str:
    return date.strftime("%Y%m%d")


class DataLoader:
    def __init__(self) -> None:
        self.industry_query = IndustryInfoQuery()
        self.stock_query = StockQuery()
        self.industry_dao = IndustryHistoryDAO()
        self.stock_dao = StockHistoryDAO()

    def load_industry_history_last_4m(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
        if end_date is None:
            end_date = _yyyymmdd(datetime.now())
        if start_date is None:
            start_date = _yyyymmdd(datetime.now() - timedelta(days=120))

        # 批量查询所有板块历史数据
        try:
            df_all = self.industry_query.get_board_industry_hist(INDUSTRY_SECTORS, start_date, end_date, False)
            if df_all is not None and not df_all.empty:
                # 批量查询返回的数据包含 industry 列，按 industry 分组并分别保存
                if 'industry' in df_all.columns:
                    for industry in INDUSTRY_SECTORS:
                        df_industry = df_all[df_all['industry'] == industry].copy()
                        if not df_industry.empty:
                            # 移除 industry 列以便保存（upsert_dataframe 会重新添加）
                            df_industry = df_industry.drop(columns=['industry'], errors='ignore')
                            try:
                                self.industry_dao.upsert_dataframe(industry, df_industry)
                            except Exception:
                                # 忽略单个板块保存失败，继续处理其他板块
                                continue
        except Exception:
            # 如果批量查询失败，降级为逐个查询
            for industry in INDUSTRY_SECTORS:
                try:
                    df = self.industry_query.get_board_industry_hist(industry, start_date, end_date, False)
                    if df is None or isinstance(df, pd.DataFrame) and df.empty:
                        continue
                    self.industry_dao.upsert_dataframe(industry, df)
                except Exception:
                    # 忽略单个板块失败，继续处理其他板块
                    continue

    def load_stock_history_last_4m(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
        if end_date is None:
            end_date = _yyyymmdd(datetime.now())
        if start_date is None:
            start_date = _yyyymmdd(datetime.now() - timedelta(days=120))

        stocks_df = self.stock_query.get_all_stock()
        if stocks_df is None or stocks_df.empty:
            return

        code_col = 'code' if 'code' in stocks_df.columns else None
        if code_col is None:
            for c in stocks_df.columns:
                if c.lower() in ("code", "symbol"):
                    code_col = c
                    break
        if code_col is None:
            return

        # 去重代码列表
        codes = stocks_df[code_col].dropna().astype(str).unique().tolist()

        # 批量查询所有股票历史数据（分批处理，避免单次查询过多）
        batch_size = 100  # 每批查询100只股票
        for i in range(0, len(codes), batch_size):
            batch_codes = codes[i:i + batch_size]
            try:
                df_all = self.stock_query.get_historical_quotes(batch_codes, start_date, end_date, False)
                if df_all is not None and not df_all.empty:
                    # 批量查询返回的数据包含 code 列，按 code 分组并分别保存
                    if 'code' in df_all.columns:
                        for code in batch_codes:
                            df_code = df_all[df_all['code'] == code].copy()
                            if not df_code.empty:
                                # 移除 code 列以便保存（upsert_dataframe 会重新添加）
                                df_code = df_code.drop(columns=['code'], errors='ignore')
                                try:
                                    self.stock_dao.upsert_dataframe(code, df_code)
                                except Exception:
                                    # 忽略单只股票保存失败，继续处理其他代码
                                    continue
            except Exception:
                # 如果批量查询失败，降级为逐个查询
                for code in batch_codes:
                    try:
                        df = self.stock_query.get_historical_quotes(code, start_date, end_date, False)
                        if df is None or isinstance(df, pd.DataFrame) and df.empty:
                            continue
                        self.stock_dao.upsert_dataframe(code, df)
                    except Exception:
                        # 忽略单只股票失败，继续处理其他代码
                        continue


