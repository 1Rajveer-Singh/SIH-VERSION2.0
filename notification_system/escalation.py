"""
Alert escalation and routing system
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class EscalationLevel(Enum):
    LEVEL_1 = "level_1"  # Site operators
    LEVEL_2 = "level_2"  # Site supervisors
    LEVEL_3 = "level_3"  # Regional managers
    LEVEL_4 = "level_4"  # Emergency services

@dataclass
class EscalationRule:
    """
    Rule for alert escalation
    """
    severity: str
    initial_level: EscalationLevel
    escalation_time_minutes: int
    max_level: EscalationLevel
    auto_escalate: bool = True
    require_acknowledgment: bool = True

class AlertEscalationManager:
    """
    Manages alert escalation based on severity and response times
    """
    
    def __init__(self):
        # Define escalation rules
        self.escalation_rules = {
            'low': EscalationRule(
                severity='low',
                initial_level=EscalationLevel.LEVEL_1,
                escalation_time_minutes=60,
                max_level=EscalationLevel.LEVEL_2,
                require_acknowledgment=False
            ),
            'medium': EscalationRule(
                severity='medium',
                initial_level=EscalationLevel.LEVEL_1,
                escalation_time_minutes=30,
                max_level=EscalationLevel.LEVEL_3,
                require_acknowledgment=True
            ),
            'high': EscalationRule(
                severity='high',
                initial_level=EscalationLevel.LEVEL_1,
                escalation_time_minutes=15,
                max_level=EscalationLevel.LEVEL_4,
                require_acknowledgment=True
            ),
            'critical': EscalationRule(
                severity='critical',
                initial_level=EscalationLevel.LEVEL_1,
                escalation_time_minutes=5,
                max_level=EscalationLevel.LEVEL_4,
                require_acknowledgment=True,
                auto_escalate=True
            )
        }
        
        # Contact groups for each escalation level
        self.contact_groups = {
            EscalationLevel.LEVEL_1: [
                {
                    'name': 'Site Operator 1',
                    'email': 'operator1@mining-site.com',
                    'phone': '+1234567890',
                    'role': 'Site Operator'
                },
                {
                    'name': 'Site Operator 2', 
                    'email': 'operator2@mining-site.com',
                    'phone': '+1234567891',
                    'role': 'Site Operator'
                }
            ],
            EscalationLevel.LEVEL_2: [
                {
                    'name': 'Site Supervisor',
                    'email': 'supervisor@mining-site.com',
                    'phone': '+1234567892',
                    'role': 'Site Supervisor'
                },
                {
                    'name': 'Safety Manager',
                    'email': 'safety@mining-site.com',
                    'phone': '+1234567893',
                    'role': 'Safety Manager'
                }
            ],
            EscalationLevel.LEVEL_3: [
                {
                    'name': 'Regional Manager',
                    'email': 'regional@mining-company.com',
                    'phone': '+1234567894',
                    'role': 'Regional Manager'
                },
                {
                    'name': 'Operations Director',
                    'email': 'operations@mining-company.com',
                    'phone': '+1234567895',
                    'role': 'Operations Director'
                }
            ],
            EscalationLevel.LEVEL_4: [
                {
                    'name': 'Emergency Services',
                    'email': 'emergency@local-gov.com',
                    'phone': '+911',
                    'role': 'Emergency Response'
                },
                {
                    'name': 'CEO',
                    'email': 'ceo@mining-company.com',
                    'phone': '+1234567896',
                    'role': 'Chief Executive Officer'
                }
            ]
        }
        
        # Track active escalations
        self.active_escalations = {}
    
    def initiate_escalation(self, alert: Dict) -> Dict:
        """
        Initiate escalation process for an alert
        """
        try:
            alert_id = alert.get('id')
            severity = alert.get('severity', 'medium')
            
            # Get escalation rule
            rule = self.escalation_rules.get(severity)
            if not rule:
                logger.warning(f"No escalation rule found for severity: {severity}")
                rule = self.escalation_rules['medium']  # Default
            
            # Create escalation record
            escalation = {
                'alert_id': alert_id,
                'current_level': rule.initial_level,
                'rule': rule,
                'started_at': datetime.utcnow(),
                'last_escalated_at': datetime.utcnow(),
                'acknowledgments': [],
                'notifications_sent': [],
                'is_resolved': False
            }
            
            self.active_escalations[alert_id] = escalation
            
            # Send initial notifications
            notification_result = self._send_level_notifications(alert, rule.initial_level)
            escalation['notifications_sent'].append({
                'level': rule.initial_level,
                'timestamp': datetime.utcnow(),
                'result': notification_result
            })
            
            # For critical alerts, immediately escalate to all levels
            if severity == 'critical':
                self._escalate_critical_alert(alert, escalation)
            
            logger.info(f"Escalation initiated for alert {alert_id} at level {rule.initial_level}")
            
            return {
                'escalation_id': alert_id,
                'initial_level': rule.initial_level.value,
                'contacts_notified': len(self.contact_groups.get(rule.initial_level, [])),
                'next_escalation_in': rule.escalation_time_minutes,
                'status': 'initiated'
            }
            
        except Exception as e:
            logger.error(f"Error initiating escalation for alert {alert.get('id')}: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def check_escalations(self) -> List[Dict]:
        """
        Check active escalations and escalate if necessary
        """
        escalations_updated = []
        current_time = datetime.utcnow()
        
        for alert_id, escalation in list(self.active_escalations.items()):
            if escalation['is_resolved']:
                continue
            
            rule = escalation['rule']
            time_since_last = (current_time - escalation['last_escalated_at']).total_seconds() / 60
            
            # Check if escalation is needed
            if (time_since_last >= rule.escalation_time_minutes and 
                escalation['current_level'] != rule.max_level):
                
                # Check if acknowledgment is required and received
                if rule.require_acknowledgment and not escalation['acknowledgments']:
                    # Escalate to next level
                    next_level = self._get_next_level(escalation['current_level'])
                    if next_level and next_level != escalation['current_level']:
                        self._escalate_to_level(alert_id, escalation, next_level)
                        escalations_updated.append({
                            'alert_id': alert_id,
                            'escalated_to': next_level.value,
                            'timestamp': current_time
                        })
                elif not rule.require_acknowledgment:
                    # Auto-escalate without acknowledgment requirement
                    next_level = self._get_next_level(escalation['current_level'])
                    if next_level and next_level != escalation['current_level']:
                        self._escalate_to_level(alert_id, escalation, next_level)
                        escalations_updated.append({
                            'alert_id': alert_id,
                            'escalated_to': next_level.value,
                            'timestamp': current_time
                        })
        
        return escalations_updated
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Record alert acknowledgment
        """
        try:
            escalation = self.active_escalations.get(alert_id)
            if not escalation:
                logger.warning(f"No active escalation found for alert {alert_id}")
                return False
            
            acknowledgment = {
                'acknowledged_by': acknowledged_by,
                'acknowledged_at': datetime.utcnow(),
                'level': escalation['current_level']
            }
            
            escalation['acknowledgments'].append(acknowledgment)
            
            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by} at level {escalation['current_level']}")
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    def resolve_escalation(self, alert_id: str, resolved_by: str) -> bool:
        """
        Mark escalation as resolved
        """
        try:
            escalation = self.active_escalations.get(alert_id)
            if not escalation:
                logger.warning(f"No active escalation found for alert {alert_id}")
                return False
            
            escalation['is_resolved'] = True
            escalation['resolved_at'] = datetime.utcnow()
            escalation['resolved_by'] = resolved_by
            
            logger.info(f"Escalation for alert {alert_id} resolved by {resolved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving escalation for alert {alert_id}: {e}")
            return False
    
    def _escalate_critical_alert(self, alert: Dict, escalation: Dict):
        """
        Immediately escalate critical alerts to all levels
        """
        for level in [EscalationLevel.LEVEL_2, EscalationLevel.LEVEL_3, EscalationLevel.LEVEL_4]:
            notification_result = self._send_level_notifications(alert, level)
            escalation['notifications_sent'].append({
                'level': level,
                'timestamp': datetime.utcnow(),
                'result': notification_result
            })
        
        escalation['current_level'] = EscalationLevel.LEVEL_4
        logger.info(f"Critical alert {alert.get('id')} escalated to all levels immediately")
    
    def _escalate_to_level(self, alert_id: str, escalation: Dict, level: EscalationLevel):
        """
        Escalate to specific level
        """
        # Get alert details (in real implementation, fetch from database)
        alert = {'id': alert_id, 'severity': 'high', 'title': 'Escalated Alert'}
        
        notification_result = self._send_level_notifications(alert, level)
        
        escalation['current_level'] = level
        escalation['last_escalated_at'] = datetime.utcnow()
        escalation['notifications_sent'].append({
            'level': level,
            'timestamp': datetime.utcnow(),
            'result': notification_result
        })
        
        logger.info(f"Alert {alert_id} escalated to level {level}")
    
    def _send_level_notifications(self, alert: Dict, level: EscalationLevel) -> Dict:
        """
        Send notifications to contacts at specific escalation level
        """
        contacts = self.contact_groups.get(level, [])
        results = {
            'emails_sent': 0,
            'sms_sent': 0,
            'total_contacts': len(contacts),
            'failed_contacts': []
        }
        
        for contact in contacts:
            try:
                # Simulate sending notifications
                logger.info(f"ESCALATION NOTIFICATION (Demo Mode):")
                logger.info(f"Level: {level.value}")
                logger.info(f"Contact: {contact['name']} ({contact['role']})")
                logger.info(f"Email: {contact['email']}")
                logger.info(f"Phone: {contact['phone']}")
                logger.info(f"Alert: {alert.get('title', 'Safety Alert')}")
                
                # In real implementation, use notification manager
                results['emails_sent'] += 1
                if contact.get('phone'):
                    results['sms_sent'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to notify {contact['name']}: {e}")
                results['failed_contacts'].append(contact['name'])
        
        return results
    
    def _get_next_level(self, current_level: EscalationLevel) -> Optional[EscalationLevel]:
        """
        Get next escalation level
        """
        level_order = [
            EscalationLevel.LEVEL_1,
            EscalationLevel.LEVEL_2,
            EscalationLevel.LEVEL_3,
            EscalationLevel.LEVEL_4
        ]
        
        try:
            current_index = level_order.index(current_level)
            if current_index < len(level_order) - 1:
                return level_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def get_escalation_status(self, alert_id: str) -> Optional[Dict]:
        """
        Get current escalation status for an alert
        """
        escalation = self.active_escalations.get(alert_id)
        if not escalation:
            return None
        
        return {
            'alert_id': alert_id,
            'current_level': escalation['current_level'].value,
            'started_at': escalation['started_at'],
            'last_escalated_at': escalation['last_escalated_at'],
            'acknowledgments_count': len(escalation['acknowledgments']),
            'notifications_sent_count': len(escalation['notifications_sent']),
            'is_resolved': escalation['is_resolved'],
            'time_active_minutes': (datetime.utcnow() - escalation['started_at']).total_seconds() / 60
        }

# Global escalation manager instance
escalation_manager = AlertEscalationManager()

def initiate_alert_escalation(alert: Dict) -> Dict:
    """
    Main function to initiate alert escalation
    """
    return escalation_manager.initiate_escalation(alert)

def check_and_escalate_alerts() -> List[Dict]:
    """
    Check and escalate alerts as needed
    """
    return escalation_manager.check_escalations()

def acknowledge_alert_escalation(alert_id: str, acknowledged_by: str) -> bool:
    """
    Acknowledge an escalated alert
    """
    return escalation_manager.acknowledge_alert(alert_id, acknowledged_by)

def resolve_alert_escalation(alert_id: str, resolved_by: str) -> bool:
    """
    Resolve an escalated alert
    """
    return escalation_manager.resolve_escalation(alert_id, resolved_by)