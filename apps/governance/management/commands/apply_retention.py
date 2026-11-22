from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.audit.models import AuditEvent
from apps.institutions.models import Institution
from apps.learning.models import Conversation, Message
def fields(model):
    return {f.name for f in model._meta.fields}
class Command(BaseCommand):
    help = "Delete audit and conversation data older than each institution's retention_days."
    def handle(self, *args, **o):
        now = timezone.localtime()
        for inst in Institution.objects.all():
            days = getattr(inst, "retention_days", 365) or 365
            cutoff = now - timedelta(days=days)
            af = fields(AuditEvent)
            aq = AuditEvent.objects.filter(institution=inst)
            if "created_at" in af:
                aq = aq.filter(created_at__lt=cutoff)
            a_del = aq.delete()[0]
            cf = fields(Conversation)
            cq = Conversation.objects.filter(institution=inst)
            if "created_at" in cf:
                cq = cq.filter(created_at__lt=cutoff)
            c_del = cq.delete()[0]
            mf = fields(Message)
            m_del = 0
            if "conversation" in mf:
                mq = Message.objects.filter(conversation__institution=inst)
                if "created_at" in mf:
                    mq = mq.filter(created_at__lt=cutoff)
                m_del = mq.delete()[0]
            try:
                AuditEvent.objects.create(institution=inst, actor=None, action="RETENTION_APPLIED",
                                          resource_type="Institution", resource_id=str(inst.id),
                                          metadata={"days": days, "audit": a_del, "conversations": c_del, "messages": m_del})
            except Exception:
                pass
            self.stdout.write(self.style.SUCCESS("%s: retention %dd -> audit=%d conversations=%d messages=%d" % (inst.name, days, a_del, c_del, m_del)))
