from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from posts.forms import PostForm
from posts.models import Group, Post, User, Comment, Follow
from .constants import (TITLE, SLUG, DESCRIPTION, TEXT, PUB_DATE, TITLE_2,
                        SLUG_2, DESCRIPTION_2, NEW_URL, INDEX_URL, AUTHOR_URL,
                        TECH_URL, NOT_FOUND_URL, SERVER_ERROR_URL)


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='VasiaBasov')
        cls.user_other = User.objects.create_user(username='PetrBasov')
        cls.authorized_client_user = Client()
        cls.authorized_client_user_other = Client()
        cls.authorized_client_user.force_login(cls.user)
        cls.authorized_client_user_other.force_login(cls.user_other)

        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )

        cls.second_group = Group.objects.create(
            title=TITLE_2,
            slug=SLUG_2,
            description=DESCRIPTION_2,
        )

        cls.post = Post.objects.create(
            text=TEXT,
            pub_date=PUB_DATE,
            author=cls.user,
            group=cls.group,
        )

        cls.form = PostForm()
        cls.GROUP_URL = reverse('group', kwargs={'slug': 'test'})
        cls.SECOND_GROUP_URL = reverse('group',
                                       kwargs={'slug': 'second-slug'})
        cls.USER_URL = reverse('profile', args=(cls.user.username,))
        cls.POST_URL = reverse('post', kwargs={'username': cls.user,
                                               'post_id': cls.post.id})
        cls.EDIT_AUTHOR = reverse('post_edit', args=(cls.user.username,
                                                     cls.post.id))

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': INDEX_URL,
            'new.html': NEW_URL,
            'group.html': self.GROUP_URL,
            'about/author.html': AUTHOR_URL,
            'about/tech.html': TECH_URL,
            'misc/404.html': NOT_FOUND_URL,
            'misc/500.html': SERVER_ERROR_URL,
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client_user.get(NEW_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client_user.get(self.GROUP_URL)
        self.assertEqual(response.context.get('group').title,
                         'Тестовый заголовок')
        self.assertEqual(response.context.get('group').description,
                         'Описание тестовой группы')
        self.assertEqual(response.context.get('group').slug, 'test')

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client_user.get(INDEX_URL)
        post_text_0 = response.context.get('page')[0].text
        post_author_0 = response.context.get('page')[0].author.username
        self.assertEqual(post_text_0, 'Тестовый тест')
        self.assertEqual(post_author_0, 'VasiaBasov')

    def test_post_with_group_anailable_in_index_page(self):
        """Если при создании поста указать группу,
        то этот пост появляется на главной странице."""
        response = self.authorized_client_user.get(INDEX_URL)
        post_group_0 = response.context.get('page')[0].group.title
        self.assertEqual(post_group_0, 'Тестовый заголовок')

    def test_post_with_group_anailable_in_group_slug_page(self):
        """Если при создании поста указать группу,
        то этот пост появляется на странице выбранной группы."""
        response = self.authorized_client_user.get(self.GROUP_URL)
        post_group_0 = response.context.get('page')[0].group.title
        self.assertEqual(post_group_0, 'Тестовый заголовок')

    def test_post_not_in_group(self):
        """Тестовый пост не появился на странице second_group."""
        response = self.authorized_client_user.get(self.SECOND_GROUP_URL)
        self.assertEqual(len(response.context['page']), 0)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client_user.get(self.USER_URL)
        expected_post = self.post
        actual_post = response.context.get('page')[0]
        self.assertEqual(actual_post, expected_post)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client_user.get(self.POST_URL)
        expected_post = self.post
        actual_post = response.context.get('post')
        self.assertEqual(actual_post, expected_post)

    def test_first_page_contains_ten_posts(self):
        """Страница содержит 10 постов."""
        for post in range(14):
            Post.objects.create(
                text=f'Такст на 14 постов {post}',
                author=get_user_model().objects.create(
                    username=f'Bloger{post}'),
            )
        response = self.authorized_client_user.get(INDEX_URL)
        self.assertEqual(len(response.context.get('page')), 10)

    def test_about_author_url_exists_at_desired_location(self):
        """Страница /author/ доступна любому пользователю."""
        response = self.guest_client.get(AUTHOR_URL)
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url_exists_at_desired_location(self):
        """Страница /tech/ доступна любому пользователю."""
        response = self.guest_client.get(TECH_URL)
        self.assertEqual(response.status_code, 200)

    def test_404_url_exists_at_desired_location(self):
        """Страница /404/ доступна любому пользователю."""
        response = self.guest_client.get(NOT_FOUND_URL)
        self.assertEqual(response.status_code, 404)

    def test_500_url_exists_at_desired_location(self):
        """Страница /500/ доступна любому пользователю."""
        response = self.guest_client.get(SERVER_ERROR_URL)
        self.assertEqual(response.status_code, 500)

    def test_user_user_can_subscribe_and_delete(self):
        """Проверка подписки и отписки от автора постов."""
        self.authorized_client_user.get(reverse(
            'profile_follow', kwargs={'username': self.user_other}))
        self.authorized_client_user.get(
            reverse('profile_unfollow',
                    kwargs={'username': self.user_other}))
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.user_other
        ).exists())

    def test_post_new_follow(self):
        """Новая запись появляется в ленте."""
        Follow.objects.create(
            user=self.user_other,
            author=self.user,
        )
        response = self.authorized_client_user_other.get(
            reverse('follow_index')
        )
        self.assertIn(self.post, response.context['page'])

    def test_authorized_client_can_comment(self):
        """Комментарии авторизованного пользователя
           отображаются в посте."""
        form_data = {'text': 'Коммент'}
        comments = Comment.objects.count()
        comment = Comment.objects.create(
            text='Коммент',
            author=self.user,
            post=self.post,
        )
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(Comment.objects.count(), comments+1)
        self.assertEqual(comment.post, self.post)
