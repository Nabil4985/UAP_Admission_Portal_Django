from django.test import TestCase, Client
from django.urls import reverse

from .models import Department, Application


class AdmissionAppTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_index_view_renders(self):
		resp = self.client.get(reverse('admission:index'))
		self.assertEqual(resp.status_code, 200)
		
		self.assertTemplateUsed(resp, 'admission/index.html')

	def test_admission_info_returns_departments(self):
		d1 = Department.objects.create(code='CSE', name='Computer Science', total_credits=120, per_credit_fee=100, seats=10)
		d2 = Department.objects.create(code='EEE', name='Electrical', total_credits=120, per_credit_fee=90, seats=8)
		resp = self.client.get(reverse('admission:admission_info'))
		self.assertEqual(resp.status_code, 200)
		self.assertIn('departments', resp.context)
		codes = [d.code for d in resp.context['departments']]
		
		self.assertEqual(codes, sorted(codes))

	def test_application_create_post_creates_application(self):
		dept = Department.objects.create(code='CSE', name='Computer Science', total_credits=120, per_credit_fee=100, seats=10)
		data = {
			'full_name': 'Test Applicant',
			'email': 'applicant@example.com',
			'phone': '0123456789',
			'department': str(dept.pk),
			'program': 'bachelors',
		}
		resp = self.client.post(reverse('admission:application_create'), data, follow=True)
		# should redirect back to apply page (follow=True gives final 200)
		self.assertEqual(resp.status_code, 200)
		self.assertTrue(Application.objects.filter(email='applicant@example.com').exists())
		app = Application.objects.get(email='applicant@example.com')
		self.assertEqual(app.full_name, 'Test Applicant')
		self.assertEqual(app.department, dept)
