import pytest
from django.conf import settings
from django.urls import reverse
from django.test import Client
from django.utils import timezone
from django.utils.timezone import timedelta

from news.models import Comment, News
from news.pytest_tests.constans import COMMENT_TEXT


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )


@pytest.fixture
def create_news():
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def create_comments(django_user_model):
    news = News.objects.create(title='Тестовая новость', text='Просто текст.')
    author = django_user_model.objects.create(username='Комментатор')
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(username='Мимо Крокодил')


@pytest.fixture
def auth_client(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))
