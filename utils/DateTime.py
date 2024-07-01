def clip(value, min_value, max_value):
    return max(min(value, max_value), min_value)

class DateTime:
    # Constants
    MONTH_MIN = 1
    MONTH_MAX = 12
    DAY_MIN = 1
    def day_max(month, year):
        if month == 2:
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                return 29
            return 28
        if month in [4, 6, 9, 11]:
            return 30
        return 31
    HOUR_MIN = 0
    HOUR_MAX = 23
    MINUTE_MIN = 0
    MINUTE_MAX = 59
    SECOND_MIN = 0
    SECOND_MAX = 59
    NANOSECOND_MIN = 0
    NANOSECOND_MAX = 999999999

    # Constructor
    def __init__(self, year, month, day, hour, minute, second, nanosecond):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.nanosecond = nanosecond

    # default methods
    def __str__(self):
        return f"{self.year}-{self.month}-{self.day} {self.hour}:{self.minute}:{self.second}.{self.nanosecond}"
    def __repr__(self):
        return f"{self.year}-{self.month}-{self.day} {self.hour}:{self.minute}:{self.second}.{self.nanosecond}"
    def __eq__(self, other):
        return self.year == other.year and self.month == other.month and self.day == other.day and self.hour == other.hour and self.minute == other.minute and self.second == other.second and self.nanosecond == other.nanosecond
    def __ne__(self, other):
        return not self.__eq__(other)
    def __lt__(self, other):
        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        if self.day != other.day:
            return self.day < other.day
        if self.hour != other.hour:
            return self.hour < other.hour
        if self.minute != other.minute:
            return self.minute < other.minute
        if self.second != other.second:
            return self.second < other.second
        return self.nanosecond < other.nanosecond
    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)
    def __gt__(self, other):
        return not self.__le__(other)
    def __ge__(self, other):
        return not self.__lt__(other)
    # Getters
    def get_year(self):
        return self.year
    def get_month(self):
        return self.month
    def get_day(self):
        return self.day
    def get_hour(self):
        return self.hour
    def get_minute(self):
        return self.minute
    def get_second(self):
        return self.second
    def get_nanosecond(self):
        return self.nanosecond
    
    # Update, the arguments are optional
    def update(self, *args):
        # retrieve the arguments
        if len(args) == 1:
            sanitized_ns = clip(args[0], DateTime.NANOSECOND_MIN, DateTime.NANOSECOND_MAX)
            self.nanosecond += sanitized_ns
        if len(args) == 2:
            sanitized_ns = clip(args[1], DateTime.NANOSECOND_MIN, DateTime.NANOSECOND_MAX)
            sanitized_s = clip(args[0], DateTime.SECOND_MIN, DateTime.SECOND_MAX)
            self.second += sanitized_s
            self.nanosecond += sanitized_ns
        if len(args) == 3:
            sanitized_ns = clip(args[2], DateTime.NANOSECOND_MIN, DateTime.NANOSECOND_MAX)
            sanitized_s = clip(args[1], DateTime.SECOND_MIN, DateTime.SECOND_MAX)
            sanitized_m = clip(args[0], DateTime.MINUTE_MIN, DateTime.MINUTE_MAX)
            self.minute += sanitized_m
            self.second += sanitized_s
            self.nanosecond += sanitized_ns
        if len(args) == 4:
            sanitized_ns = clip(args[3], DateTime.NANOSECOND_MIN, DateTime.NANOSECOND_MAX)
            sanitized_s = clip(args[2], DateTime.SECOND_MIN, DateTime.SECOND_MAX)
            sanitized_m = clip(args[1], DateTime.MINUTE_MIN, DateTime.MINUTE_MAX)
            sanitized_h = clip(args[0], DateTime.HOUR_MIN, DateTime.HOUR_MAX)
            self.hour += sanitized_h
            self.minute += sanitized_m
            self.second += sanitized_s
            self.nanosecond += sanitized_ns
        # check for overflow
        if self.nanosecond > DateTime.NANOSECOND_MAX:
            self.nanosecond -= DateTime.NANOSECOND_MAX
            self.second += 1
        if self.second > DateTime.SECOND_MAX:
            self.second -= DateTime.SECOND_MAX
            self.minute += 1
        if self.minute > DateTime.MINUTE_MAX:
            self.minute -= DateTime.MINUTE_MAX
            self.hour += 1
        if self.hour > DateTime.HOUR_MAX:
            self.hour -= DateTime.HOUR_MAX
            self.day += 1
        if self.day > DateTime.day_max(self.month, self.year):
            self.day -= DateTime.day_max(self.month, self.year)
            self.month += 1
        if self.month > DateTime.MONTH_MAX:
            self.month -= DateTime.MONTH_MAX
            self.year += 1
    


            

