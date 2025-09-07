import psycopg2
import socket

# Force IPv4
family = socket.AF_INET

conn = psycopg2.connect(
    host='db.rzktipnfmqrhpqtlfixp.supabase.co',
    port=5432,
    user='postgres',
    password='JQPqdT71xwfFrmgr',
    database='postgres',
    connect_timeout=10
)
print('✅ Successfully connected!')
conn.close()
