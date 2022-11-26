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
