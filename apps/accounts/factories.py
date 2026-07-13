import factory
from apps.accounts.models import CustomUser


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    role = CustomUser.Role.CLIENT

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or "testpass123"
        self.set_password(password)
        if create:
            self.save()


class ClientFactory(UserFactory):
    role = CustomUser.Role.CLIENT


class FreelancerFactory(UserFactory):
    role = CustomUser.Role.FREELANCER