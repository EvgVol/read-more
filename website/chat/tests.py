from io import BytesIO

from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from PIL import Image

from courses.models.course import Course
from courses.models.subject import Subject

from website.asgi import application

User = get_user_model()


def _tiny_image():
    buffer = BytesIO()
    Image.new('RGB', (10, 10), color='white').save(buffer, format='PNG')
    return SimpleUploadedFile('img.png', buffer.getvalue(),
                               content_type='image/png')


def _make_course(title='Python Basics', owner=None):
    subject = Subject.objects.create(
        title='Dev', description='Development', image=_tiny_image())
    course = Course(title=title, owner=owner, subject=subject,
                image=_tiny_image(), period=8, count_projects=1)
    course.save()
    return course


class TestCourseChatRoom(TestCase):
    """Tests for the course_chat_room view."""

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student', email='s@example.com', password='pass123')
        self.other = User.objects.create_user(
            username='outsider', email='o@example.com', password='pass123')
        self.course = _make_course(owner=self.student)

    def test_room_requires_login(self):
        response = self.client.get(
            reverse('chat:course_chat_room', args=[self.course.id]))
        self.assertEqual(response.status_code, 302)

    def test_room_forbidden_for_non_student(self):
        self.client.login(username='outsider', password='pass123')
        response = self.client.get(
            reverse('chat:course_chat_room', args=[self.course.id]))
        self.assertEqual(response.status_code, 403)

    def test_room_for_student(self):
        self.course.students.add(self.student)
        self.client.login(username='student', password='pass123')
        response = self.client.get(
            reverse('chat:course_chat_room', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['course'], self.course)

    def test_room_unknown_course_forbidden(self):
        self.client.login(username='outsider', password='pass123')
        response = self.client.get(
            reverse('chat:course_chat_room', args=[99999]))
        self.assertEqual(response.status_code, 403)


class TestChatConsumer(TransactionTestCase):
    """Tests for the ChatConsumer websocket consumer.

    TransactionTestCase (not TestCase) because the websocket runs in
    another thread where TestCase's uncommitted transaction is
    invisible and its DB connection is closed.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='wsstudent', email='ws@example.com', password='pass123')
        self.course = _make_course('Ws Course', owner=self.user)
        self.course.students.add(self.user)

    def _session_cookie(self):
        client = Client()
        client.login(username='wsstudent', password='pass123')
        return f'sessionid={client.session.session_key}'

    def _communicator(self, cookie):
        return WebsocketCommunicator(
            application, f'/ws/chat/room/{self.course.id}/',
            headers=[
                (b'cookie', cookie.encode()),
                (b'origin', b'http://testserver'),
            ])

    def test_authenticated_connect_and_broadcast(self):
        cookie = self._session_cookie()

        async def scenario():
            communicator = self._communicator(cookie)
            connected, _ = await communicator.connect()
            self.assertTrue(connected)
            await communicator.send_json_to({'message': 'hello'})
            response = await communicator.receive_json_from(timeout=5)
            self.assertEqual(response['message'], 'hello')
            self.assertEqual(response['user'], 'wsstudent')
            await communicator.disconnect()

        async_to_sync(scenario)()

    def test_two_clients_broadcast_between_them(self):
        cookie = self._session_cookie()

        async def scenario():
            communicator_a = self._communicator(cookie)
            connected, _ = await communicator_a.connect()
            self.assertTrue(connected)

            communicator_b = self._communicator(cookie)
            connected, _ = await communicator_b.connect()
            self.assertTrue(connected)

            await communicator_a.send_json_to({'message': 'ping'})
            # both clients receive the broadcast (group_send)
            msg_a = await communicator_a.receive_json_from(timeout=5)
            msg_b = await communicator_b.receive_json_from(timeout=5)
            self.assertEqual(msg_a['message'], 'ping')
            self.assertEqual(msg_b['message'], 'ping')
            await communicator_a.disconnect()
            await communicator_b.disconnect()

        async_to_sync(scenario)()

    def test_anonymous_connect_rejected(self):
        """No session cookie -> consumer must refuse the handshake."""

        async def scenario():
            # no cookie headers at all
            communicator = WebsocketCommunicator(
                application, f'/ws/chat/room/{self.course.id}/',
                headers=[
                    (b'origin', b'http://testserver'),
                ])
            connected, _ = await communicator.connect()
            self.assertFalse(connected)

        async_to_sync(scenario)()

    def test_non_student_connect_rejected(self):
        """Authenticated but not enrolled -> consumer must refuse."""
        outsider = User.objects.create_user(
            username='wsoutsider', email='wso@example.com',
            password='pass123')
        client = Client()
        client.login(username='wsoutsider', password='pass123')
        cookie = f'sessionid={client.session.session_key}'

        async def scenario():
            communicator = self._communicator(cookie)
            connected, _ = await communicator.connect()
            self.assertFalse(connected)

        async_to_sync(scenario)()