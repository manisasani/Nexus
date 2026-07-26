import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:
    @staticmethod
    def send_otp_sms(phone_number, otp_code):
        if settings.SMS_BACKEND == "console":
            print(f"[SMS SANDBOX] To: {phone_number} | Your OTP code is: {otp_code}")
            logger.info(f"[SMS SANDBOX] OTP sent to phone ending in ...{phone_number[-4:]}")
        elif settings.SMS_BACKEND == "twilio":
            SMSService._send_via_twilio(phone_number, otp_code)
        else:
            raise ValueError(f"Unknown SMS_BACKEND: {settings.SMS_BACKEND}")

    @staticmethod
    def _send_via_twilio(phone_number, otp_code):
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        try:
            client.messages.create(
                body=f"Your Nexus verification code is: {otp_code}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number,
            )
            logger.info(f"Twilio SMS sent to phone ending in ...{phone_number[-4:]}")
        except Exception as exc:
            logger.error(f"Twilio SMS failed: {exc}")
            raise