from datetime import datetime

def get_sample_candidates():
    """Return real candidates data for the election"""
    return [
        {
            "name": "Olukunle Tomiwa Covenant",
            "position": "President",
            "faculty": "Natural and Applied Science",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Kennedy Solomon", 
            "position": "President",
            "faculty": "Natural and Applied Science",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Jeremiah Gideon Emmanuel",
            "position": "President",
            "faculty": "Natural and Applied Science",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Onwuoha Confidence Daberechi",
            "position": "Vice President",
            "faculty": "Natural and Applied Science",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Babade Beatrice Jonathan",
            "position": "Vice President",
            "faculty": "Arts and Communications",
            "created_at": datetime.utcnow()
        }
    ]