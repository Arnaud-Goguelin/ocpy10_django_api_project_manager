import factory

from faker import Faker

from issue.models import Comment, Issue
from project.models import Project
from user.models import User


fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    date_of_birth = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)
    consent = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password properly using set_password() and attach plain password"""
        if not create:
            return

        # Use extracted password if provided, otherwise generate random
        if extracted:
            password = extracted
        else:
            password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
        obj.set_password(password)
        obj.save()

        # Attach plain password to the object for easy testing
        obj.plain_password = password


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
        skip_postgeneration_save = True

    name = factory.Faker("catch_phrase")
    description = factory.Faker("text", max_nb_chars=200)
    type = factory.Faker("random_element", elements=[*Project.ProjectTypes])
    # Do not forget to set author manually as Factory directly create instance in DB not using serializer which
    # usually set the author automatically

    @factory.post_generation
    def contributors(self, create, extracted, **kwargs):
        """Add contributors to the project"""
        if not create:
            return

        if self.author:
            self.contributors.add(self.author)

        # Add additional contributors if provided
        if extracted:
            for contributor in extracted:
                self.contributors.add(contributor)


class IssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Issue

    title = factory.Faker("sentence")
    content = factory.Faker("text")
    status = factory.Faker("random_element", elements=[*Issue.Status])
    priority = factory.Faker("random_element", elements=[*Issue.Priority])
    tags = factory.Faker("random_element", elements=[*Issue.Tags])
    project = factory.SubFactory(ProjectFactory)
    # Do not forget to set author manually as Factory directly create instance in DB not using serializer which
    # usually set the author automatically


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    content = factory.Faker("text")
    issue = factory.SubFactory(IssueFactory)
    # Do not forget to set author manually as Factory directly create instance in DB not using serializer which
    # usually set the author automatically
