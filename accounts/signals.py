from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.utils.timezone import now
from django.dispatch import receiver

@receiver(user_logged_in)
def limit_user_sessions(sender, request, user, **kwargs):
    current_session_key = request.session.session_key

    sessions = Session.objects.filter(expire_date__gte=now())
    for session in sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id) and session.session_key != current_session_key:
            session.delete()
