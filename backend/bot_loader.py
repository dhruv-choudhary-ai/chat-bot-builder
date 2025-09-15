# bot_loader.py
from bots.retail_bot import retail_bot
from bots.telecom_bot import telecom_bot
from bots.course_enrollment_bot import course_enrollment_bot
from bots.career_counselling_bot import career_counselling_bot
from bots.lead_capturing_bot import lead_capturing_bot
from bots.insurance_bot import insurance_bot
from bots.hotel_booking_bot import hotel_booking_bot
from bots.banking_bot import banking_bot
from bots.real_estate_bot import real_estate_bot

BOTS = {
    "Retail Bot": retail_bot,
    "Telecom bot": telecom_bot,
    "Course Enrollment bot": course_enrollment_bot,
    "Career Counselling Bot": career_counselling_bot,
    "Lead Capturing Bot": lead_capturing_bot,
    "Insurance Bot": insurance_bot,
    "Hotel Booking Bot": hotel_booking_bot,
    "Banking Bot": banking_bot,
    "Real estate bot": real_estate_bot,
}

def get_bot_by_type(bot_type: str):
    return BOTS.get(bot_type)
