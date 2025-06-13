import os
import pymssql
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DB")
    username = os.getenv("AZURE_SQL_USER")
    password = os.getenv("AZURE_SQL_PASSWORD")
    return pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
        port=1433
    )

def fetch_activity_data(
    customer_id=10,
    activity_type=None,
    since_days=365
) -> pd.DataFrame:
    """
    获取指定客户最近一年的活动数据（可指定类型），为所有agent提供原始数据。
    """
    conn = get_connection()
    query = """
        SELECT ActivityID, CustomerID, Type, StartTime, EndTime, Duration,
               StartCondition, StartLocation, EndCondition, Notes
        FROM dbo.Activity
        WHERE CustomerID = %s AND StartTime >= DATEADD(day, -%s, GETDATE())
    """
    params = [customer_id, since_days]
    if activity_type:
        query += " AND Type = %s"
        params.append(activity_type)
    query += " ORDER BY StartTime ASC"
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df