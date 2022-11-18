from django.db import models

class RegisteredAdmin(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=88)

    # Zkontroluje, jestli request obsahuje 'admin' session
    @staticmethod
    def IsLoggedIn(request):
        x = request.session.get('admin')
        return bool(x)

    # Temporary řešení - vytvoření defaultního admina
    @staticmethod
    def CreateDefaultAdmin():
        from django.contrib.auth.hashers import make_password
        admin = RegisteredAdmin(
            first_name='Default',
            last_name='Admin',
            email='test@test.com',
            password=make_password("123456")
        )
        admin.save()
