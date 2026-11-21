from apps.accounts.models import User
from apps.institutions.models import Institution, Membership
# 1. Create or get the user
u, created = User.objects.get_or_create(username='Caristus_Mugendi', defaults={'role': 'school_admin'})
u.set_password('admin12345!')
u.save()
print('USER READY:', u.username)
# 2. Create or get the school
inst, _ = Institution.objects.get_or_create(name='Jifunze Test School', defaults={'country': 'Kenya'})
print('SCHOOL READY:', inst.name)
# 3. Link user to school
Membership.objects.get_or_create(user=u, institution=inst, defaults={'role': 'school_admin'})
print('MEMBERSHIP LINKED')
