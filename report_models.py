class MemberAttendance:
    first_name: str
    last_name: str
    # The number of unique days that the member attended during a given period
    early_period_attendance: int
    # The number of unique days that a member's attendance was recorded as either true or false
    early_period_record_count: int
    # The number of unique days that the member attended during a given period
    late_period_attendance: int
    # The number of unique days that a member's attendance was recorded as either true or false
    late_period_record_count: int

    def early_period_frequency(self) -> float:
        if self.early_period_record_count == 0:
            return 0.0
        else:
            return self.early_period_attendance / self.early_period_record_count

    def late_period_frequency(self) -> float:
        if self.late_period_record_count == 0:
            return 0.0
        else:
            return self.late_period_attendance / self.late_period_record_count

    def frequency_change(self) -> float :
        return self.late_period_frequency() - self.early_period_frequency()