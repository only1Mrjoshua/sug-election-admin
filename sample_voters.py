from datetime import datetime

def get_sample_voters():
    """Return sample voters data with ID and name system"""
    return [
        {
            "voter_id": "V2024001",
            "full_name": "John Chukwuma Adebayo",
            "has_voted": False,
            "registration_date": datetime.utcnow()
        },
        {
            "voter_id": "V2024002", 
            "full_name": "Grace Ngozi Okoro",
            "has_voted": False,
            "registration_date": datetime.utcnow()
        },
        {
            "voter_id": "V2024003",
            "full_name": "Michael Oluwaseun Bello",
            "has_voted": False,
            "registration_date": datetime.utcnow()
        },
        {
            "voter_id": "V2024004",
            "full_name": "Sarah Temitope Johnson",
            "has_voted": False,
            "registration_date": datetime.utcnow()
        },
        {
            "voter_id": "V2024005",
            "full_name": "David Ifeanyi Mohammed",
            "has_voted": False,
            "registration_date": datetime.utcnow()
        }
    ]