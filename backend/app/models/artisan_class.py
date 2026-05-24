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


class Customer(User):
    def __init__(self, name, phone, address, city):
        super().__init__(name, phone)
        self.address = address
        self.city = city
        self.bookings = []

    def make_booking(self, artisan, date):
        booking = {"artisan": artisan, "date": date}
        self.bookings.append(booking)
        return f"Booking created for {self.name} with {artisan.name} on {date}"

    def get_bookings(self):
        return self.bookings
