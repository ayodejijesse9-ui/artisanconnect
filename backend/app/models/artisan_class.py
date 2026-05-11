class Artisan:
    def __init__(self, name, skill, city):
        self.name = name
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