class User:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone
    
    def get_contact(self):
        return f"Name: {self.name} — Phone: {self.phone}"


class Artisan(User):
    def __init__(self, name, phone, skill, city):
        super().__init__(name, phone)
        self.skill = skill
        self.city = city
        self.verified = False
        self.rating = 0.0
        self.jobs_completed = 0

    def verify(self):
        self.verified = True
        return f"{self.name} is now verified"

    def get_summary(self):
        status = "Verified" if self.verified else "Unverified"
        return f"{self.name} — {self.skill} — {self.city} — {status}"