from typing import List, Dict, Any, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings


class EmailNotificationService:
    """Service for sending email notifications to operators."""

    def __init__(self):
        # Email configuration (should be in settings)
        self.smtp_host = getattr(settings, 'smtp_host', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_user = getattr(settings, 'smtp_user', None)
        self.smtp_password = getattr(settings, 'smtp_password', None)
        self.from_email = getattr(settings, 'from_email', 'noreply@aperture.dev')

    async def send_pattern_discovery_email(
        self,
        to_email: str,
        discovered_patterns: List[Dict[str, Any]],
        lookback_days: int = 7
    ) -> bool:
        """
        Send email notification about discovered patterns.

        Args:
            to_email: Recipient email address
            discovered_patterns: List of discovered pattern suggestions
            lookback_days: Days analyzed

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.smtp_user or not self.smtp_password:
            print("SMTP not configured. Email notifications disabled.")
            return False

        subject = f"🎯 Aperture discovered {len(discovered_patterns)} new user patterns"

        # Build HTML email body
        html_body = self._build_discovery_email_html(discovered_patterns, lookback_days)

        try:
            return await self._send_email(to_email, subject, html_body)
        except Exception as e:
            print(f"Error sending discovery email: {e}")
            return False

    def _build_discovery_email_html(
        self,
        patterns: List[Dict[str, Any]],
        lookback_days: int
    ) -> str:
        """Build HTML email body for pattern discovery notification."""

        patterns_html = ""
        for i, pattern in enumerate(patterns[:5], 1):  # Show top 5
            patterns_html += f"""
            <div style="background: #f9f9f9; border-left: 4px solid #667eea; padding: 20px; margin: 15px 0; border-radius: 4px;">
                <h3 style="margin: 0 0 10px 0; color: #333;">{i}. {pattern.get('name', 'Unnamed Pattern')}</h3>
                <p style="color: #666; margin: 5px 0;">
                    <strong>Description:</strong> {pattern.get('description', 'No description')}
                </p>
                <p style="color: #666; margin: 5px 0;">
                    <strong>Detected in:</strong> {pattern.get('detected_in', 'Unknown')}
                </p>
                <p style="color: #666; margin: 5px 0;">
                    <strong>Confidence:</strong> {int(pattern.get('confidence', 0) * 100)}%
                </p>

                <div style="margin-top: 10px;">
                    <strong style="color: #667eea;">Value Proposition:</strong>
                    <p style="color: #555; margin: 5px 0 0 0;">
                        {pattern.get('value_proposition', 'Track this pattern to better understand your users')}
                    </p>
                </div>

                <div style="margin-top: 15px;">
                    <a href="https://api.aperture.dev/admin/constructs/enable?pattern={i}"
                       style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">
                        ✓ Enable Tracking
                    </a>
                    <a href="https://api.aperture.dev/admin/patterns/{i}/details"
                       style="background: #f0f0f0; color: #333; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin-left: 10px;">
                        View Details
                    </a>
                </div>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 24px;">🎯 New User Patterns Discovered</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">
                    We analyzed your conversations from the past {lookback_days} days
                </p>
            </div>

            <div style="margin-bottom: 30px;">
                <p style="font-size: 16px; color: #555;">
                    Hi there! 👋
                </p>
                <p style="font-size: 16px; color: #555;">
                    Aperture has discovered <strong>{len(patterns)} new patterns</strong> in your user conversations.
                    These patterns could help you better understand and personalize experiences for your users.
                </p>
            </div>

            <h2 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                Discovered Patterns
            </h2>

            {patterns_html}

            <div style="background: #f0f7ff; border: 1px solid #667eea; border-radius: 8px; padding: 20px; margin-top: 30px;">
                <h3 style="margin: 0 0 10px 0; color: #667eea;">💡 What's Next?</h3>
                <ul style="color: #555; margin: 0; padding-left: 20px;">
                    <li>Click "Enable Tracking" to start monitoring these patterns</li>
                    <li>Once enabled, you'll see historical data backfilled automatically</li>
                    <li>Use these insights for personalization and analytics</li>
                </ul>
            </div>

            <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #999; font-size: 12px;">
                <p>
                    Sent by <a href="https://aperture.dev" style="color: #667eea;">Aperture</a> - User Intelligence for AI Apps
                </p>
                <p>
                    <a href="https://aperture.dev/settings/notifications" style="color: #999;">Manage email preferences</a>
                </p>
            </div>

        </body>
        </html>
        """

        return html

    async def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """
        Send an email using SMTP.

        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML email body

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            print(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    async def send_weekly_digest(
        self,
        to_email: str,
        user_stats: Dict[str, Any],
        top_assessments: List[Dict[str, Any]]
    ) -> bool:
        """
        Send weekly digest email with user analytics summary.

        Args:
            to_email: Recipient email
            user_stats: Overall statistics
            top_assessments: Top assessments this week

        Returns:
            True if sent successfully
        """
        subject = "📊 Your Weekly Aperture Digest"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>📊 Weekly Digest</h2>

            <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>This Week's Numbers</h3>
                <ul>
                    <li><strong>Total Conversations:</strong> {user_stats.get('conversations', 0)}</li>
                    <li><strong>Assessments Extracted:</strong> {user_stats.get('assessments', 0)}</li>
                    <li><strong>Active Users:</strong> {user_stats.get('users', 0)}</li>
                    <li><strong>Average Confidence:</strong> {user_stats.get('avg_confidence', 0):.2f}</li>
                </ul>
            </div>

            <h3>Top Insights</h3>
            <p>Most common user patterns this week:</p>

            {self._format_top_assessments(top_assessments)}

            <p style="margin-top: 30px;">
                <a href="https://api.aperture.dev/admin/dashboard"
                   style="background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                    View Full Dashboard
                </a>
            </p>
        </body>
        </html>
        """

        try:
            return await self._send_email(to_email, subject, html_body)
        except Exception as e:
            print(f"Error sending weekly digest: {e}")
            return False

    def _format_top_assessments(self, assessments: List[Dict[str, Any]]) -> str:
        """Format top assessments for email."""
        html = "<ul>"
        for assessment in assessments[:5]:
            html += f"<li><strong>{assessment.get('element', 'Unknown')}:</strong> {assessment.get('description', 'No description')}</li>"
        html += "</ul>"
        return html


# Singleton instance
email_service = EmailNotificationService()
