"""
Dual-Channel 2FA OTP Service
Manages 6-digit cryptographically secure OTP generation, 5-minute TTL expiration,
and dual-channel delivery via Email (SMTP / SendGrid) and SMS (Twilio / Firebase Phone Auth).
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..database.firestore_client import db_client

logger = logging.getLogger("memorybox.otp")


class OTPService:
    def __init__(self):
        self.otp_ttl_minutes = 5
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", "no-reply@memorybox.vault")
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_number = os.getenv("TWILIO_PHONE_NUMBER", "")

    def generate_otp(self) -> str:
        """Generates a 6-digit cryptographically random OTP string."""
        return f"{secrets.randbelow(900000) + 100000}"

    async def issue_dual_channel_otp(
        self,
        uid: str,
        email: str,
        phone: str,
        name: str = "Family Member"
    ) -> Dict[str, Any]:
        """
        Generates and dispatches 2FA OTPs to both Email and SMS channels.
        Stores the record in Firestore under otps/{uid} with 5-minute TTL.
        """
        # Generate 6-digit OTPs (can be same or distinct; user can enter either)
        email_otp = self.generate_otp()
        phone_otp = self.generate_otp()

        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=self.otp_ttl_minutes)

        otp_record = {
            "uid": uid,
            "email_otp": email_otp,
            "phone_otp": phone_otp,
            "email": email,
            "phone": phone,
            "createdAt": now.isoformat(),
            "expiresAt": expires_at.isoformat()
        }

        # Save to Firestore under otps/{uid}
        await db_client.save_otp(uid, otp_record)

        # Dispatch via Email Channel
        email_sent = await self._send_email_otp(email=email, name=name, otp=email_otp)

        # Dispatch via SMS Channel
        sms_sent = await self._send_sms_otp(phone=phone, otp=phone_otp)

        print(f"\n[OTP DEBUG] Generated Dual-Channel OTP for {uid}: Email OTP: {email_otp} | SMS OTP: {phone_otp}\n")
        logger.info(
            f"Dual-Channel OTP issued for user {uid}. "
            f"Email sent: {email_sent}, SMS sent: {sms_sent}, TTL: {self.otp_ttl_minutes}m."
        )

        return {
            "uid": uid,
            "email_dispatched": email_sent,
            "sms_dispatched": sms_sent,
            "expires_in_minutes": self.otp_ttl_minutes,
            "debug_email_otp": email_otp,
            "debug_phone_otp": phone_otp
        }

    async def verify_otp(self, uid: str, entered_otp: str) -> Tuple[bool, str]:
        """
        Validates the entered OTP code.
        Accepts if entered OTP matches either the email OTP OR the phone OTP.
        Enforces 5-minute TTL expiration.
        """
        clean_otp = entered_otp.strip()
        record = await db_client.get_otp(uid)

        if not record:
            return False, "No active OTP request found. Please request a new OTP."

        # Check expiration (TTL 5 minutes)
        try:
            expires_at = datetime.fromisoformat(record["expiresAt"])
            if datetime.utcnow() > expires_at:
                await db_client.delete_otp(uid)
                return False, "OTP has expired (validity is 5 minutes). Please request a new code."
        except Exception as e:
            logger.error(f"Error parsing OTP expiration: {e}")

        # Check match against Email OTP OR Phone OTP
        email_otp = str(record.get("email_otp", ""))
        phone_otp = str(record.get("phone_otp", ""))

        if clean_otp in (email_otp, phone_otp):
            # One-time use: delete after successful verification
            await db_client.delete_otp(uid)
            return True, "Dual-channel 2FA verified successfully."

        return False, "Invalid OTP code. Please check the code sent to your email or mobile phone."

    async def _send_email_otp(self, email: str, name: str, otp: str) -> bool:
        """Sends OTP via SMTP (Gmail / SendGrid) or logs in development."""
        subject = f"Your MemoryBox Security Code: {otp}"
        html_body = f"""
        <div style="font-family: Georgia, serif; max-width: 500px; margin: auto; padding: 20px; border: 1px solid #d4af37; background: #fffaf0; border-radius: 8px;">
            <h2 style="color: #5c4033; font-style: italic;">MemoryBox Heritage Vault</h2>
            <p style="color: #5c4033; font-size: 16px;">Hello {name},</p>
            <p style="color: #5c4033;">Your single-use 2FA verification code to access the digital family heritage vault is:</p>
            <div style="text-align: center; margin: 24px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #8c6d1f; background: #f5e6ca; padding: 10px 24px; border-radius: 4px; border: 1px dashed #d4af37;">
                    {otp}
                </span>
            </div>
            <p style="color: #7a5c48; font-size: 13px;">This code is valid for 5 minutes. If you did not request this, please ignore this email.</p>
        </div>
        """

        if self.smtp_user and self.smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = self.smtp_from
                msg["To"] = email
                msg.attach(MIMEText(html_body, "html"))

                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.smtp_from, [email], msg.as_string())
                logger.info(f"OTP email sent to {email}")
                return True
            except Exception as e:
                logger.error(f"Failed to dispatch live SMTP email to {email}: {e}")

        # Development / Fallback logger
        logger.info(f"[DEV 2FA EMAIL] To: {email} | OTP: {otp}")
        return True

    async def _send_sms_otp(self, phone: str, otp: str) -> bool:
        """Sends OTP via Twilio / Firebase Phone Auth or logs in development."""
        message_body = f"Your MemoryBox 2FA security code is: {otp}. Valid for 5 minutes."

        if self.twilio_sid and self.twilio_token and self.twilio_number:
            try:
                from twilio.rest import Client
                client = Client(self.twilio_sid, self.twilio_token)
                client.messages.create(
                    body=message_body,
                    from_=self.twilio_number,
                    to=phone
                )
                logger.info(f"OTP SMS dispatched to {phone}")
                return True
            except Exception as e:
                logger.error(f"Twilio SMS dispatch failure: {e}")

        # Development / Fallback logger
        logger.info(f"[DEV 2FA SMS] To: {phone} | SMS OTP: {otp}")
        return True


# Global singleton instance
otp_service = OTPService()
