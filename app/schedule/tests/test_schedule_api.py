"""
Tests for the Schedule API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Lesson,
    Schedule
)

from schedule.serializers import ScheduleSerializer


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_schedule(user, **params):
    """Create and return a sample schedule"""
    defaults = {
        'name': 'Sample schedule',
    }
    defaults.update(params)

    schedule = Schedule.objects.create(user=user, **defaults)
    lesson = Lesson.objects.create(
        name='Lesson1',
        room='Room1',
        start_time='9:15',
        end_time='10:15',
        day='MON',
        user=user,
        )
    schedule.lessons.add(lesson)
    return schedule


class PublicScheduleAPITest(TestCase):
    """Test unauthenticated schedule API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get('/api/schedule/schedules/')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateScheduleAPITest(TestCase):
    """Test authenticated schedule API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_schedules(self):
        """Test retrieving a list of schedules"""
        create_schedule(user=self.user)

        res = self.client.get('/api/schedule/schedules/')

        schedules = Schedule.objects.all().order_by('id')
        serializer = ScheduleSerializer(schedules, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_schedules_limited_to_user(self):
        """Test that schedules for the authenticated user are returned"""
        user2 = create_user(email='other@example.com',
                            password='test123')
        create_schedule(user=user2)
        create_schedule(user=self.user)

        res = self.client.get('/api/schedule/schedules/')

        schedules = Schedule.objects.filter(user=self.user)
        serializer = ScheduleSerializer(schedules, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_create_schedule(self):
        """Test creating a new schedule"""
        payload = {
            'user': 'user@example.com',
            'name': 'Sample schedule',
            'lessons': [
                {
                    'name': 'Lesson1',
                    'room': 'Room1',
                    'start_time': '9:15',
                    'end_time': '10:15',
                    'day': 'MON',
                },
                {
                    'name': 'Lesson2',
                    'room': 'Room2',
                    'start_time': '10:15',
                    'end_time': '11:15',
                    'day': 'MON',
                }
            ]
        }
        res = self.client.post('/api/schedule/schedules/',
                               payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        schedule = Schedule.objects.get(id=res.data['id'])
        self.assertEqual(schedule.lessons.count(), 2)
        self.assertEqual(schedule.name, payload['name'])
        self.assertEqual(
            schedule.lessons.first().name,
            payload['lessons'][0]['name']
        )

    def test_update_schedule(self):
        """Test updating a schedule"""
        schedule = create_schedule(user=self.user)
        payload = {
            'name': 'New schedule',
        }
        url = '/api/schedule/schedules/{0}/'.format(schedule.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        schedule.refresh_from_db()
        self.assertEqual(schedule.name, payload['name'])

    def test_delete_schedule(self):
        """Test deleting a schedule"""
        schedule = create_schedule(user=self.user)
        url = '/api/schedule/schedules/{0}/'.format(schedule.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Schedule.objects.count(), 0)
