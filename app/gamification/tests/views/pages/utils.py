from app.gamification.models import CustomUser


class LogInUser:

    @classmethod
    def create_user(cls, andrew_id, password, is_superuser=False):
        kwargs = {
            'andrew_id': andrew_id,
            'password': password,
            'email': '%s@example.com' % andrew_id,
        }

        if is_superuser:
            user = CustomUser.objects.create_superuser(**kwargs)
        else:
            user = CustomUser.objects.create_user(**kwargs)

        return user

    @classmethod
    def createAndLogInUser(cls, client, andrew_id, password, is_superuser=False):
        cls.create_user(andrew_id, password, is_superuser)
        client.login(andrew_id=andrew_id, password=password)
