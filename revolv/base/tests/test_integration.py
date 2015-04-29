from bs4 import BeautifulSoup
from django.contrib.auth import authenticate
from django.core import mail
from django.test import TestCase
from django_webtest import WebTest
from revolv.lib.testing import TestUserMixin, WebTestMixin
from revolv.project.models import Project


class DashboardTestCase(TestUserMixin, TestCase):
    DASH_BASE = "/dashboard/"
    ADMIN_DASH = "/dashboard/admin/"
    AMBAS_DASH = "/dashboard/ambassador/"
    DONOR_DASH = "/dashboard/donor/"
    HOME_URL = "/"

    def test_dash_redirects(self):
        """Test that the dashboard links redirect to the correct dashboard levels."""
        response = self.client.get(self.DASH_BASE, follow=True)
        self.assertRedirects(response, self.HOME_URL)

        self.send_test_user_login_request()
        self.test_profile.make_administrator()
        response = self.client.get(self.DASH_BASE, follow=True)
        self.assertRedirects(response, self.ADMIN_DASH)

        self.test_profile.make_ambassador()
        response = self.client.get(self.DASH_BASE, follow=True)
        self.assertRedirects(response, self.AMBAS_DASH)

        self.test_profile.make_donor()
        response = self.client.get(self.DASH_BASE, follow=True)
        self.assertRedirects(response, self.DONOR_DASH)


class AuthIntegrationTest(TestUserMixin, WebTest):
    def test_forgot_password_flow(self):
        """Test that the entire forgot password flow works."""
        response = self.app.get("/login/").maybe_follow()
        reset_page_response = response.click(linkid="reset").maybe_follow()
        self.assertTemplateUsed(reset_page_response, "base/auth/forgot_password_initial.html")

        form = reset_page_response.forms["password_reset_form"]
        self.assertEqual(form.method, "post")

        # email should not be sent if we don't have a user with that email
        form["email"] = "something@idontexist.com"
        unregistered_email_response = form.submit().maybe_follow()
        self.assertTemplateUsed(unregistered_email_response, "base/auth/forgot_password_done.html")
        self.assertEqual(len(mail.outbox), 0)

        form["email"] = self.test_user.email
        registered_email_response = form.submit().maybe_follow()
        self.assertTemplateUsed(registered_email_response, "base/auth/forgot_password_done.html")
        self.assertEqual(len(mail.outbox), 1)

        query = BeautifulSoup(mail.outbox[0].body)
        # we want to make sure that there is a password reset link (not just a url) in the email
        link = query.find(id="reset_password_link")
        self.assertIsNotNone(link)

        confirm_url = link["href"]
        confirm_response = self.app.get(confirm_url).maybe_follow()
        self.assertEqual(confirm_response.context["validlink"], True)

        form = confirm_response.forms["password_reset_confirm_form"]
        form["new_password1"] = "test_new_password"
        form["new_password2"] = "test_new_password"
        success_response = form.submit().maybe_follow()
        self.assertEqual(success_response.status_code, 200)
        self.bust_test_user_cache()
        result = authenticate(username=self.test_user.username, password="test_new_password")
        self.assertEqual(result, self.test_user)


class DashboardIntegrationTest(TestUserMixin, WebTest, WebTestMixin):
    csrf_checks = False

    def assert_logged_in_user_can_create_project_via_dashboard(self, tagline):
        project = Project.factories.base.build(tagline=tagline)

        dashboard_response = self.app.get("/dashboard/").maybe_follow()
        create_page_response = dashboard_response.click(linkid="create_project").maybe_follow()
        project_form = create_page_response.forms["project_form"]
        project_form = self.fill_form_from_model(project_form, project)
        dashboard_new_project_response = project_form.submit().maybe_follow()
        self.assertEqual(dashboard_new_project_response.status_code, 200)

        created_project = Project.objects.get(tagline=tagline)
        self.assertEqual(created_project.project_status, Project.DRAFTED)
        self.assert_in_response_html(dashboard_new_project_response, "project-%d" % created_project.pk)

    def test_create_new_project_via_dashboard(self):
        """Test that an ambassador can create a new project via the dashboard."""
        self.test_profile.make_ambassador()
        self.send_test_user_login_request(webtest=True)

        self.assert_logged_in_user_can_create_project_via_dashboard("this_project_made_by_ambsaddador")

        self.test_profile.make_administrator()
        self.send_test_user_login_request(webtest=True)
        self.assert_logged_in_user_can_create_project_via_dashboard("this_project_made_by_ambsaddador")

    def test_admin_can_approve_drafted_project(self):
        # amb_user = User.objects.create_user(username="amb", password="amb_pass")
        # admin_user = User.objects.create_user(username="admin", password="admin_pass")
        # ambassador = RevolvUserProfile.factories.create()
        # TODO: do this function lol
        pass

    def test_admin_can_deny_drafted_project(self):
        pass

    def test_admin_can_complete_active_project(self):
        pass

    def test_post_updates_for_active_and_completed_projects(self):
        pass

    def test_ambassador_cant_see_other_ambassadors_projects(self):
        pass
