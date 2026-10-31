"""sql/queries.sql dosyasını "-- Q<n>:" işaretlerine göre bölüp çalıştırır."""
import re
import sqlite3
from pathlib import Path

import pandas as pd

from load_db import DB

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "sql" / "queries.sql"

_BLOCK = re.compile(r"^-- (Q\d+): (.+?)$\n(.*?;)", re.S | re.M)


def parse_queries(path: Path = QUERIES) -> dict[str, tuple[str, str]]:
    """{"Q1": (soru, sql), ...}"""
    return {qid: (question.strip(), sql.strip()) for qid, question, sql in _BLOCK.findall(path.read_text())}


def run(qid: str, db_path: Path = DB) -> pd.DataFrame:
    _, sql = parse_queries()[qid]
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(sql, con)


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    for qid, (question, _) in parse_queries().items():
        result = run(qid)
        print(f"== {qid}: {question} ({len(result):,} satır)")
        print(result.head(20).to_string(index=False), "\n")
