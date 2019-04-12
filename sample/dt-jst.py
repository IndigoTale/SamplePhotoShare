from datetime import datetime, timedelta, timezone


JST = timezone(timedelta(hours=+9), 'JST')

jst_now_str = datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')

print(type(jst_now_str),jst_now_str)