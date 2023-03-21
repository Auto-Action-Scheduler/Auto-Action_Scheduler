import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from actionapp.models import Action


# Create your tests here.

class ActionTests(APITestCase):
    def create_actions(self, name, schedule_time, created_by, actions):
        return Action.active_objects.create(name=name, schedule_time=schedule_time, created_by=created_by,
                                            actions=actions)

    def create_sms(self, name, action_type, description, created_by, schedule_time, sms_sender, phone_number):
        return Action.objects.create(name=name, action_type=action_type, description=description, created_by=created_by,
                                     schedule_time=schedule_time, sms_sender=sms_sender, phone_number=phone_number)

    def create_reminder(self, name, action_type, description, created_by, schedule_time, email):
        return Action.objects.create(name=name, action_type=action_type, description=description, created_by=created_by,
                                     schedule_time=schedule_time, email=email)

    def get_user(self):
        username = "demo"
        password = "password@1"
        self.user = User.objects.create_user(username, password=password)
        data = {
            "username": username,
            "password": password
        }
        url = reverse('token_obtain_pair')
        response = self.client.post(url, data=data, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return {'user_id': self.user.id, 'HTTP_AUTHORIZATION=': f'Bearer {token}', 'user': self.user}

    def test_create_mail(self):
        url = reverse('create-list')
        response = self.client.post(url, data={'name': 'Testing', 'actions': [{
            'subject': 'Mail Subject',
            'description': 'mail body',
            'email': 'oyedeleyusuff@gmail.com',
            'receiver_mail': ['yoyedele@afexnigeria.com'],
            'action_type': 'Mail'
        }],
                                               'schedule_time': timezone.now() + datetime.timedelta(days=1),
                                               'created_by': self.get_user()['user_id']}, format='json')
        # print(response.data['data']['id'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'actions')
        return response.data

    def test_list_actions(self):
        url = reverse('create-list')

        response = self.client.get(url, format='json', **self.get_user())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertQuerysetEqual(Action.active_objects.all(), response.data)

    def test_create_sms(self):
        url = reverse('create-list')

        response = self.client.post(url, data={'name': 'Testing', 'actions': [{
            'description': 'mail body',
            'phone_number': ['+2347063704879'],
            'action_type': 'SMS',
            'sms_sender': 'yusuf'
        }],
                                               'schedule_time': timezone.now() + datetime.timedelta(days=1),
                                               'created_by': self.get_user()['user_id']}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'actions')

    def test_reminder_authorization(self):
        url = reverse('create-list')

        response = self.client.post(url, data={'name': 'Testing', 'actions': [{
            'description': 'mail body',
            'email': 'oyedeleyusuff@gmail.com',
            'action_type': 'Reminder',
        }],
                                               'schedule_time': timezone.now() + datetime.timedelta(days=1),
                                               'created_by': self.get_user()['user_id']}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'actions')

    def test_update_action(self):
        user = self.get_user()
        create_action = self.create_actions(name='Test', schedule_time=timezone.now() + datetime.timedelta(days=1),
                                            created_by=user['user'], actions=[{
                'subject': 'Mail Subject',
                'description': 'mail body',
                'email': 'oyedeleyusuff@gmail.com',
                'receiver_mail': ['yoyedele@afexnigeria.com'],
                'action_type': 'Mail',
                'is_executed': 'false'
            },
                {
                    'description': 'mail body',
                    'phone_number': ['+2347063704879'],
                    'action_type': 'SMS',
                    'sms_sender': 'yusuf',
                    'is_executed': 'false'
                },
                {
                    'description': 'mail body',
                    'email': 'oyedeleyusuff@gmail.com',
                    'action_type': 'Reminder',
                }])
        url = reverse('retrieve-update-destroy', args=[create_action.id])
        response = self.client.put(url, data={'name': 'Testing',
                                              'schedule_time': timezone.now() + datetime.timedelta(days=1),
                                              'created_by': user['user_id'],
                                              'actions': [{
                                                  'subject': 'Mail Subject update',
                                                  'description': 'mail body update',
                                                  'email': 'oyedeleyusuff@gmail.com',
                                                  'receiver_mail': ['yoyedele@afexnigeria.com'],
                                                  'action_type': 'Mail'
                                              },
                                                  {
                                                      'description': 'mail body update',
                                                      'phone_number': ['+2347063704879'],
                                                      'action_type': 'SMS',
                                                      'sms_sender': 'yusuf',
                                                      'is_executed': 'false'
                                                  },
                                                  {
                                                      'description': 'mail body update',
                                                      'email': 'oyedeleyusuff@gmail.com',
                                                      'action_type': 'Reminder',
                                                  }]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'actions')

    # def test_update_sms(self):
    #     user = self.get_user()
    #
    #     create_sms = self.create_sms(name='Test SMS', action_type='SMS', description='sms body',
    #                                  created_by=user['user'], schedule_time=timezone.now() + datetime.timedelta(days=1),
    #                                  sms_sender='goodie', phone_number=['+2347063704879'])
    #
    #     url = reverse('retrieve-update-destroy', args=[create_sms.id])
    #     response = self.client.put(url,
    #                                data={'name': 'Test SMS Update', 'action_type': 'SMS', 'description': 'sms body',
    #                                      'created_by': user['user_id'],
    #                                      'schedule_time': timezone.now() + datetime.timedelta(days=1),
    #                                      'sms_sender': 'goodie', 'phone_number': ['+2347063704879']},
    #                                format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertContains(response, 'phone_number')
    #
    # def test_update_reminder(self):
    #     user = self.get_user()
    #     create_reminder = self.create_reminder(name='Test', action_type='Reminder', description='reminder body',
    #                                            created_by=user['user'],
    #                                            schedule_time=timezone.now() + datetime.timedelta(days=1),
    #                                            email='oyedeleyusuff@gmail.com')
    #     url = reverse('retrieve-update-destroy', args=[create_reminder.id])
    #     response = self.client.put(url, data={'name': 'Test', 'action_type': 'Reminder', 'description': 'reminder body',
    #                                           'created_by': user['user_id'],
    #                                           'schedule_time': timezone.now() + datetime.timedelta(days=1),
    #                                           'email': 'oyedeleyusuff@gmail.com'}, format='json')
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertContains(response, 'email')
    #
    def test_retrieve_actions(self):
        user = self.get_user()
        create_action = self.create_actions(name='Test', schedule_time=timezone.now() + datetime.timedelta(days=1),
                                            created_by=user['user'], actions=[{
                'subject': 'Mail Subject',
                'description': 'mail body',
                'email': 'oyedeleyusuff@gmail.com',
                'receiver_mail': ['yoyedele@afexnigeria.com'],
                'action_type': 'Mail',
                'is_executed': 'false'
            },
                {
                    'description': 'mail body',
                    'phone_number': ['+2347063704879'],
                    'action_type': 'SMS',
                    'sms_sender': 'yusuf',
                    'is_executed': 'false'
                },
                {
                    'description': 'mail body',
                    'email': 'oyedeleyusuff@gmail.com',
                    'action_type': 'Reminder',
                }])
        url = reverse('retrieve-update-destroy', args=[create_action.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertQuerysetEqual(Action.active_objects.get(id=user['user_id']), [user['user']])

    #
    # def test_retrieve_sms(self):
    #     user = self.get_user()
    #
    #     create_sms = self.create_sms(name='Test SMS', action_type='SMS', description='sms body',
    #                                  created_by=user['user'], schedule_time='2023-03-07T18:55:29.118928+01:00',
    #                                  sms_sender='goodie', phone_number=['+2347063704879'])
    #
    #     url = reverse('retrieve-update-destroy', args=[create_sms.id])
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_retrieve_reminder(self):
    #     user = self.get_user()
    #     create_reminder = self.create_reminder(name='Test', action_type='Reminder', description='reminder body',
    #                                            created_by=user['user'],
    #                                            schedule_time='2023-03-07T18:55:29.118928+01:00',
    #                                            email='oyedeleyusuff@gmail.com')
    #     url = reverse('retrieve-update-destroy', args=[create_reminder.id])
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_actions(self):
        user = self.get_user()
        create_action = self.create_actions(name='Test', schedule_time=timezone.now() + datetime.timedelta(days=1),
                                            created_by=user['user'], actions=[{
                'subject': 'Mail Subject',
                'description': 'mail body',
                'email': 'oyedeleyusuff@gmail.com',
                'receiver_mail': ['yoyedele@afexnigeria.com'],
                'action_type': 'Mail',
                'is_executed': 'false'
            },
                {
                    'description': 'mail body',
                    'phone_number': ['+2347063704879'],
                    'action_type': 'SMS',
                    'sms_sender': 'yusuf',
                    'is_executed': 'false'
                },
                {
                    'description': 'mail body',
                    'email': 'oyedeleyusuff@gmail.com',
                    'action_type': 'Reminder',
                }])
        url = reverse('retrieve-update-destroy', args=[create_action.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_delete_sms(self):
    #     user = self.get_user()
    #
    #     create_sms = self.create_sms(name='Test SMS', action_type='SMS', description='sms body',
    #                                  created_by=user['user'], schedule_time=timezone.now() + datetime.timedelta(days=1),
    #                                  sms_sender='goodie', phone_number=['+2347063704879'])
    #
    #     url = reverse('retrieve-update-destroy', args=[create_sms.id])
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    # def test_delete_reminder(self):
    #     user = self.get_user()
    #     create_reminder = self.create_reminder(name='Test', action_type='Reminder', description='reminder body',
    #                                            created_by=user['user'],
    #                                            schedule_time=timezone.now() + datetime.timedelta(days=1),
    #                                            email='oyedeleyusuff@gmail.com')
    #     url = reverse('retrieve-update-destroy', args=[create_reminder.id])
    #     response = self.client.delete(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    def test_cancel_action(self):
        user = self.get_user()
        action_url = reverse('create-list')
        url = reverse('cancel-action')
        action_response = self.client.post(action_url, data={'name': 'Testing',
                                              'schedule_time': timezone.now() + datetime.timedelta(days=1),
                                              'created_by': user['user_id'],
                                              'actions': [{
                                                  'subject': 'Mail Subject update',
                                                  'description': 'mail body update',
                                                  'email': 'oyedeleyusuff@gmail.com',
                                                  'receiver_mail': ['yoyedele@afexnigeria.com'],
                                                  'action_type': 'Mail'
                                              },
                                                  {
                                                      'description': 'mail body update',
                                                      'phone_number': ['+2347063704879'],
                                                      'action_type': 'SMS',
                                                      'sms_sender': 'yusuf',
                                                      'is_executed': 'false'
                                                  },
                                                  {
                                                      'description': 'mail body update',
                                                      'email': 'oyedeleyusuff@gmail.com',
                                                      'action_type': 'Reminder',
                                                  }]}, format='json')
        response = self.client.post(url, data={'task_id': action_response.data['task_id']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'message')

    # def test_cancel_sms(self):
    #     sms_url = reverse('create-list')
    #
    #     sms_response = self.client.post(sms_url, data={'name': 'Testing', 'action_type': 'SMS',
    #                                                    'description': 'SMS Testing',
    #                                                    'sms_sender': 'Goodie',
    #                                                    'phone_number': ['+2347063704879'],
    #                                                    'schedule_time': timezone.now() + datetime.timedelta(days=1),
    #                                                    'created_by': self.get_user()['user_id']}, format='json')
    #
    #     url = reverse('cancel-action')
    #     response = self.client.post(url, data={'task_id': sms_response.data['task_id']})
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertContains(response, 'message')
    #
    def test_create_user(self):
        url = reverse('create-list-user')
        response = self.client.post(url, data={'username': 'goodie', 'password': '153692', 'first_name': 'Yusuf',
                                               'last_name': 'Oyedele'}, format='json', **self.get_user())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_user(self):
        url = reverse('create-list-user')
        response = self.client.get(url, format='json', **self.get_user())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_create_reminder(self):
    #     auth_url = reverse('create-list')
    #
    #     auth_response = self.client.post(auth_url, data={'name': 'Testing', 'action_type': 'Reminder',
    #                                            'description': 'Reminder Testing',
    #                                            'email': 'oyedeleyusuff@gmail.com',
    #                                            'schedule_time': '2023-03-08T18:55:29.118928+01:00',
    #                                            'created_by': self.get_user()['user_id']}, format='json')
    #     print(auth_response.data)
    #     url = reverse('create-reminder')
    #     response = self.client.post(url, data={
    #         'auth_url': auth_response.data['auth_url'],
    #         'obj_id': auth_response.data['data']['id'],
    #         'user_id': auth_response.data['data']['created_by']
    #     }, format='json')
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertContains(response, 'message')
