import hashlib
from datetime import datetime,timedelta,timezone

# Create Hashed Password
def hashed_password(user_id,password,created_at):
    salt = hashlib.md5((user_id+created_at).encode()).hexdigest()
    return hashlib.sha256((salt+password).encode()).hexdigest()

# Check Filename Extension
def allowed_file(filename:str):
    ALLOWED_EXTENSIONS = ['jpg','jpeg','png','JPG','JPEG','PNG']
    return bool('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)

# Get Time Stamp
JST = timezone(timedelta(hours=+9), 'JST')
def get_cuurent_timestamp():
    return datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S.%f %Z')