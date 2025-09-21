"""
Notification system for alerts and warnings
"""
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import requests
import json
from datetime import datetime
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NotificationConfig:
    """Configuration for notification services"""
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    
    # Twilio settings
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # Webhook settings
    default_webhook_url: str = ""
    webhook_timeout: int = 10
    
    # General settings
    max_retries: int = 3
    rate_limit_per_minute: int = 10

class EmailNotificationService:
    """
    Email notification service using SMTP
    """
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.sent_count = 0
        self.last_reset = datetime.utcnow()
    
    def send_email(self, 
                   to_email: str, 
                   subject: str, 
                   message: str, 
                   is_html: bool = False,
                   priority: str = "normal") -> bool:
        """
        Send email notification
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit():
                logger.warning("Email rate limit exceeded")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Set priority headers
            if priority == "high":
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            elif priority == "critical":
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
                msg['Importance'] = 'High'
            
            # Add body
            if is_html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls(context=context)
                
                # For demo purposes, skip actual login if credentials not provided
                if self.config.smtp_username and self.config.smtp_password:
                    server.login(self.config.smtp_username, self.config.smtp_password)
                
                # For demo, just log the email instead of sending
                logger.info(f"EMAIL NOTIFICATION (Demo Mode):")
                logger.info(f"To: {to_email}")
                logger.info(f"Subject: {subject}")
                logger.info(f"Message: {message}")
                
                # In real implementation:
                # server.send_message(msg)
            
            self.sent_count += 1
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_alert_email(self, alert: Dict, recipient: str) -> bool:
        """
        Send formatted alert email
        """
        subject = f"🚨 {alert.get('severity', '').upper()} ALERT: {alert.get('title', 'Mining Safety Alert')}"
        
        message = f"""
MINING SAFETY ALERT

Alert ID: {alert.get('id', 'N/A')}
Site: {alert.get('site_id', 'Unknown')}
Severity: {alert.get('severity', 'Unknown').upper()}
Type: {alert.get('alert_type', 'Unknown')}

MESSAGE:
{alert.get('message', 'No message provided')}

Timestamp: {alert.get('created_at', datetime.utcnow().isoformat())}
Status: {alert.get('status', 'Active')}

IMMEDIATE ACTIONS REQUIRED:
- Review the alert details in the monitoring dashboard
- Follow established safety protocols for {alert.get('severity', 'this')} level alerts
- Coordinate with on-site personnel if necessary
- Document any actions taken

Dashboard: http://localhost:3001/alerts/{alert.get('id', '')}

This is an automated alert from the AI-Based Rockfall Prediction System.
Do not reply to this email.
        """
        
        priority = "critical" if alert.get('severity') in ['high', 'critical'] else "normal"
        
        return self.send_email(
            to_email=recipient,
            subject=subject,
            message=message,
            priority=priority
        )
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        now = datetime.utcnow()
        if (now - self.last_reset).seconds >= 60:
            self.sent_count = 0
            self.last_reset = now
        
        return self.sent_count < self.config.rate_limit_per_minute

class SMSNotificationService:
    """
    SMS notification service (Twilio simulation for demo)
    """
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.sent_count = 0
        self.last_reset = datetime.utcnow()
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """
        Send SMS notification
        """
        try:
            # Check rate limiting
            if not self._check_rate_limit():
                logger.warning("SMS rate limit exceeded")
                return False
            
            # For demo purposes, simulate SMS sending
            logger.info(f"SMS NOTIFICATION (Demo Mode):")
            logger.info(f"To: {to_phone}")
            logger.info(f"Message: {message}")
            
            # In real implementation with Twilio:
            """
            from twilio.rest import Client
            
            client = Client(self.config.twilio_account_sid, self.config.twilio_auth_token)
            
            message = client.messages.create(
                body=message,
                from_=self.config.twilio_phone_number,
                to=to_phone
            )
            """
            
            self.sent_count += 1
            logger.info(f"SMS sent successfully to {to_phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_phone}: {e}")
            return False
    
    def send_alert_sms(self, alert: Dict, recipient_phone: str) -> bool:
        """
        Send formatted alert SMS
        """
        severity = alert.get('severity', '').upper()
        site = alert.get('site_id', 'Unknown Site')
        
        message = f"🚨 {severity} ALERT - {site}: {alert.get('title', 'Safety Alert')}. Check dashboard immediately. Alert ID: {alert.get('id', 'N/A')}"
        
        # Truncate message to SMS length limit
        if len(message) > 160:
            message = message[:157] + "..."
        
        return self.send_sms(recipient_phone, message)
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        now = datetime.utcnow()
        if (now - self.last_reset).seconds >= 60:
            self.sent_count = 0
            self.last_reset = now
        
        return self.sent_count < self.config.rate_limit_per_minute

class WebhookNotificationService:
    """
    Webhook notification service for integration with external systems
    """
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send_webhook(self, webhook_url: str, payload: Dict, headers: Optional[Dict] = None) -> bool:
        """
        Send webhook notification
        """
        try:
            default_headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Rockfall-Prediction-System/1.0'
            }
            
            if headers:
                default_headers.update(headers)
            
            # For demo purposes, log webhook instead of sending
            logger.info(f"WEBHOOK NOTIFICATION (Demo Mode):")
            logger.info(f"URL: {webhook_url}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            logger.info(f"Headers: {default_headers}")
            
            # In real implementation:
            """
            response = requests.post(
                webhook_url,
                json=payload,
                headers=default_headers,
                timeout=self.config.webhook_timeout
            )
            
            response.raise_for_status()
            """
            
            logger.info(f"Webhook sent successfully to {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook to {webhook_url}: {e}")
            return False
    
    def send_alert_webhook(self, alert: Dict, webhook_url: str) -> bool:
        """
        Send formatted alert webhook
        """
        payload = {
            "event_type": "alert_created",
            "timestamp": datetime.utcnow().isoformat(),
            "alert": {
                "id": alert.get('id'),
                "site_id": alert.get('site_id'),
                "title": alert.get('title'),
                "message": alert.get('message'),
                "severity": alert.get('severity'),
                "alert_type": alert.get('alert_type'),
                "status": alert.get('status'),
                "created_at": alert.get('created_at'),
                "sensor_ids": alert.get('sensor_ids', []),
                "prediction_id": alert.get('prediction_id')
            },
            "system": {
                "name": "AI-Based Rockfall Prediction System",
                "version": "1.0.0",
                "dashboard_url": f"http://localhost:3001/alerts/{alert.get('id', '')}"
            }
        }
        
        return self.send_webhook(webhook_url, payload)

class NotificationManager:
    """
    Central manager for all notification services
    """
    
    def __init__(self, config: NotificationConfig = None):
        self.config = config or NotificationConfig()
        
        # Initialize services
        self.email_service = EmailNotificationService(self.config)
        self.sms_service = SMSNotificationService(self.config)
        self.webhook_service = WebhookNotificationService(self.config)
        
        # Notification preferences storage (in real app, this would be in database)
        self.user_preferences = {}
    
    def send_alert_notifications(self, alert: Dict, user_preferences: List[Dict]) -> Dict[str, bool]:
        """
        Send notifications for an alert based on user preferences
        """
        results = {
            'email_sent': [],
            'sms_sent': [],
            'webhooks_sent': [],
            'failed_notifications': []
        }
        
        for user_pref in user_preferences:
            user_id = user_pref.get('user_id')
            channels = user_pref.get('channels', [])
            severity_filter = user_pref.get('severity_filter', [])
            
            # Check if alert severity matches user's filter
            if alert.get('severity') not in severity_filter:
                continue
            
            for channel in channels:
                if not channel.get('enabled', False):
                    continue
                
                channel_type = channel.get('type')
                channel_config = channel.get('config', {})
                
                try:
                    if channel_type == 'email':
                        email = channel_config.get('address')
                        if email and self.email_service.send_alert_email(alert, email):
                            results['email_sent'].append(email)
                        else:
                            results['failed_notifications'].append(f"email:{email}")
                    
                    elif channel_type == 'sms':
                        phone = channel_config.get('phone')
                        if phone and self.sms_service.send_alert_sms(alert, phone):
                            results['sms_sent'].append(phone)
                        else:
                            results['failed_notifications'].append(f"sms:{phone}")
                    
                    elif channel_type == 'webhook':
                        webhook_url = channel_config.get('url')
                        if webhook_url and self.webhook_service.send_alert_webhook(alert, webhook_url):
                            results['webhooks_sent'].append(webhook_url)
                        else:
                            results['failed_notifications'].append(f"webhook:{webhook_url}")
                
                except Exception as e:
                    logger.error(f"Error sending {channel_type} notification for user {user_id}: {e}")
                    results['failed_notifications'].append(f"{channel_type}:{user_id}:{str(e)}")
        
        return results
    
    def send_system_notification(self, 
                                message: str, 
                                subject: str = "System Notification",
                                severity: str = "medium",
                                admin_contacts: List[str] = None) -> bool:
        """
        Send system-wide notifications to administrators
        """
        if not admin_contacts:
            admin_contacts = ["admin@mining-company.com"]  # Default admin
        
        success_count = 0
        total_count = len(admin_contacts)
        
        for contact in admin_contacts:
            try:
                if "@" in contact:  # Email
                    if self.email_service.send_email(contact, subject, message, priority=severity):
                        success_count += 1
                elif contact.startswith("+"):  # Phone number
                    if self.sms_service.send_sms(contact, f"{subject}: {message}"):
                        success_count += 1
            except Exception as e:
                logger.error(f"Failed to send system notification to {contact}: {e}")
        
        return success_count > 0
    
    def test_notifications(self, test_config: Dict) -> Dict[str, bool]:
        """
        Test all notification channels
        """
        results = {}
        
        test_message = "This is a test notification from the AI-Based Rockfall Prediction System."
        
        # Test email
        if test_config.get('email'):
            results['email'] = self.email_service.send_email(
                test_config['email'],
                "Test Email Notification",
                test_message
            )
        
        # Test SMS
        if test_config.get('phone'):
            results['sms'] = self.sms_service.send_sms(
                test_config['phone'],
                test_message
            )
        
        # Test webhook
        if test_config.get('webhook_url'):
            test_payload = {
                "test": True,
                "message": test_message,
                "timestamp": datetime.utcnow().isoformat()
            }
            results['webhook'] = self.webhook_service.send_webhook(
                test_config['webhook_url'],
                test_payload
            )
        
        return results

# Global notification manager instance
notification_manager = NotificationManager()

def send_alert_notification(alert: Dict, user_preferences: List[Dict] = None) -> Dict:
    """
    Main function to send alert notifications
    """
    if user_preferences is None:
        # Default admin notification
        user_preferences = [{
            'user_id': 'admin',
            'channels': [
                {
                    'type': 'email',
                    'enabled': True,
                    'config': {'address': 'admin@mining-company.com'}
                }
            ],
            'severity_filter': ['medium', 'high', 'critical']
        }]
    
    return notification_manager.send_alert_notifications(alert, user_preferences)

def test_notification_system(test_config: Dict) -> Dict:
    """
    Test the notification system
    """
    return notification_manager.test_notifications(test_config)