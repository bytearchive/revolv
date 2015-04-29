import datetime

import factory
from revolv.project.models import Category, Project


class ProjectFactory(factory.django.DjangoModelFactory):
    """
    Factory for default projects (drafted). Note: the cover_photo will be
    None for a default factory, because there doesn't seem to be a good way
    to import a defulat picture without having one in static files. Also, doing
    so would upload it to s3 every time a test used this factory.

    So, be careful about accessing cover_photo when using projects created
    by this factory.
    """
    class Meta:
        model = Project

    funding_goal = 50.0
    title = "Hello"
    tagline = "This project will be really cool."
    video_url = "https://www.youtube.com/watch?v=9bZkp7q19f0"
    impact_power = 50.5
    location = "Berkeley"
    end_date = datetime.date.today() - datetime.timedelta(days=1)  # tomorrow
    mission_statement = "We do solar!"
    cover_photo = None
    org_name = "Power for Community Center"
    org_about = "Community Center is a center for communities."
    org_start_date = datetime.date.today() + datetime.timedelta(days=1)  # today
    actual_energy = 25.5
    amount_repaid = 29.25
    ambassador = factory.SubFactory("revolv.base.factories.RevolvUserProfileFactory")
    location_latitude = 42.0
    location_longitude = 42.0


class ActiveProjectFactory(ProjectFactory):
    """Factory for default active projects."""
    project_status = Project.ACTIVE


class DraftedProjectFactory(ProjectFactory):
    project_status = Project.DRAFTED


class ProjectFactories(object):
    base = ProjectFactory
    active = ActiveProjectFactory
    drafted = DraftedProjectFactory


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    title = factory.Iterator(Category.valid_categories)


class CategoryFactories(object):
    base = CategoryFactory
