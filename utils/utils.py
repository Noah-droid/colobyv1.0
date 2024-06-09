from datetime import datetime, timedelta, timezone


def generate_token_lifetime(no_of_days):

    """This generates lifetime of access and refresh token"""

    current_time = datetime.now(timezone.utc)

    expires_at = current_time + timedelta(days=no_of_days)
    
    
    return expires_at.isoformat()