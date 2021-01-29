from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post, User
from . import constants as c


class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='VasiaBasov')
        cls.group = Group.objects.create(
            title=c.TITLE,
            slug=c.SLUG,
            description=c.DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=c.TEXT,
            pub_date=c.PUB_DATE,
            author=cls.user,
            group=cls.group,
        )
        cls.EDIT_URLS = reverse('post_edit', args=(cls.user.username,
                                                   cls.post.id))

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post(self):
        """При отправке формы создаётся новая запись в базе данных."""
        counter = 1
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id
        }
        self.authorized_client.post(c.NEW_URL, data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), counter + 1)

    def test_edit_post(self):
        """Тестируем изменение поста."""
        group_havent_post = Group.objects.create(
            title='test-group-2',
            slug='test_group_2',
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': group_havent_post.id,
        }
        self.authorized_client.post(self.EDIT_URLS,
                                    data=form_data,
                                    follow=True)
        post_edit = Post.objects.first()
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.author, self.user)
        self.assertEqual(post_edit.group, group_havent_post)

    def test_create_post(self):
        """Валидная форма создает post."""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=c.SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'text',
            'group': self.group.id,
            'image': uploaded,
        }
        quantity_post = Post.objects.count()
        response = self.authorized_client.post(c.NEW_URL,
                                               data=form_data,
                                               follow=True)
        self.assertEqual(Post.objects.count(), quantity_post+1)
        self.assertRedirects(response, c.INDEX_URL)
        post_new = Post.objects.exclude(id=self.post.id)[0]
        self.assertEqual(post_new.text, form_data['text'])
        self.assertEqual(post_new.group.id, form_data['group'])
        self.assertEqual(self.user, self.post.author)
