from shared.db.experts import get_experts_collections, get_timings_collection
from shared.models.common import Common
from shared.models.constants import expert_times, TimeFormats
from shared.db.schedules import get_schedules_collection
from datetime import datetime, timedelta
from bson import ObjectId
import pytz


class Slot:
    def __init__(self, expert_id, utc_date, duration):
        self.timings_collection = get_timings_collection()
        self.experts_collection = get_experts_collections()
        self.schedules_collection = get_schedules_collection()
        self.expert_id = expert_id
        self.times = expert_times
        self.utc_date = utc_date
        self.duration = duration
        self.common = Common()
        self.ist_datetime = self.convert_to_ist()
        self.day_name = self.ist_datetime.strftime("%A")
        self.slots = self.calculate_slots() or []

    def convert_to_ist(self) -> datetime:
        utc_datetime = datetime.strptime(
            self.utc_date, TimeFormats.ANTD_TIME_FORMAT)
        return utc_datetime + timedelta(hours=5, minutes=30)

    def calculate_slots(self):
        return self.slots_calculater(self.expert_id, self.day_name, self.duration)

    def to_output_slots(self) -> list:
        output_slots = []
        utc_zone = pytz.utc
        ist_timezone = pytz.timezone('Asia/Kolkata')

        for slot in self.slots:
            slot_start_str = slot.split(' - ')[0]
            slot_start_time = datetime.strptime(slot_start_str, "%H:%M").time()
            slot_start_ist = datetime.combine(
                self.ist_datetime.date(), slot_start_time)
            slot_start_utc = (slot_start_ist - timedelta(hours=5,
                              minutes=30)).replace(tzinfo=utc_zone)
            slot_start_utc_str = slot_start_utc.strftime(
                TimeFormats.ANTD_TIME_FORMAT)

            slot_dict = {
                "slot": slot,
                "datetime": slot_start_utc_str,
                "available": slot_start_utc >= datetime.now(utc_zone)
            }
            slot_dict = self.check_availability(slot_dict, slot, ist_timezone)
            off_vacation = self.common.check_vacation(
                ObjectId(self.expert_id), slot_start_utc)
            if off_vacation == False:
                slot_dict["available"] = False
            output_slots.append(slot_dict)

        return output_slots

    def check_availability(self, slot_dict, slot, ist_timezone):
        if slot_dict["available"] == False:
            return slot_dict

        expert_schedule = self.schedules_collection.find_one({
            "expert": ObjectId(self.expert_id),
            "datetime": {
                "$gte": datetime.combine(self.ist_datetime.date(), datetime.strptime(slot.split(' - ')[0], "%H:%M").time()),
                "$lt": datetime.combine(self.ist_datetime.date(), datetime.strptime(slot.split(' - ')[0], "%H:%M").time()) + timedelta(minutes=self.duration)
            }
        })

        if expert_schedule:
            scheduled_duration = expert_schedule["duration"] if "duration" in expert_schedule else 60
            if scheduled_duration in [30, 60]:
                slot_dict["available"] = False
                if scheduled_duration == 60:
                    next_slot = self.slots[self.slots.index(slot) + 1]
                    self.slots.remove(next_slot)

        utc_datetime = datetime.strptime(
            slot_dict["datetime"], TimeFormats.ANTD_TIME_FORMAT)
        ist_datetime = utc_datetime.astimezone(ist_timezone)
        ist_hour = ist_datetime.hour

        expert_doc = self.experts_collection.find_one(
            {"_id": ObjectId(self.expert_id)}, {"type": 1})
        expert_type = expert_doc["type"] if expert_doc else None

        if expert_type and expert_type in ["saarthi", "sarathi"]:
            if not (9 <= ist_hour < 22):
                slot_dict["available"] = False
        else:
            if not (10 <= ist_hour < 14) or not (16 <= ist_hour < 20):
                slot_dict["available"] = False

        return slot_dict

    def slots_calculater(self, expert_id, day: str, duration=30):
        timings = list(self.timings_collection.find(
            {"expert": ObjectId(expert_id)}))

        # Find the schedule for the specified day
        timing = next(
            (s for s in timings if str(s['day']).lower() == day.lower()), None)

        if not timing:
            print(f"No schedule found for {day}")
            return

        times = self.times

        # Generate slots for primary time
        primary_slots = self.generate_slots(
            timing[times[0]], timing[times[1]], duration) if times[0] in timing and timing[times[0]] != "" else []

        # Generate slots for secondary time, if available
        secondary_slots = self.generate_slots(
            timing[times[2]], timing[times[3]], duration) if times[2] in timing and timing[times[2]] != "" else []

        return primary_slots + secondary_slots

    def generate_slots(self, start_time_str, end_time_str, duration) -> list:
        start_time = datetime.strptime(start_time_str, '%H:%M')
        end_time = datetime.strptime(end_time_str, '%H:%M')
        slots = []

        current_time = start_time
        while current_time + timedelta(minutes=duration) <= end_time:
            end_slot_time = current_time + timedelta(minutes=duration)
            slots.append(
                f"{current_time.strftime('%H:%M')} - {end_slot_time.strftime('%H:%M')}")
            current_time = end_slot_time

        return slots
