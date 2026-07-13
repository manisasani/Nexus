import factory
from datetime import date, timedelta
from apps.projects.models import Project, Proposal
from apps.accounts.factories import ClientFactory, FreelancerFactory


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    owner = factory.SubFactory(ClientFactory)
    title = factory.Sequence(lambda n: f"Project {n}")
    description = "A test project description."
    budget = "500.00"
    deadline = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
    status = Project.Status.DRAFT


class OpenProjectFactory(ProjectFactory):
    status = Project.Status.OPEN


class ProposalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Proposal

    project = factory.SubFactory(OpenProjectFactory)
    freelancer = factory.SubFactory(FreelancerFactory)
    cover_letter = "I can do this job well."
    bid_amount = "400.00"
    status = Proposal.Status.PENDING