import pytest
from django.conf import settings
from django.urls import reverse

from news.models import Comment, News
from news import forms


@pytest.mark.django_db
def test_home_page(client, create_news):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200
    assert (response.context['object_list'].count()
            == settings.NEWS_COUNT_ON_HOME_PAGE)


@pytest.mark.django_db
def test_news_order(client, create_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_detail_page(client, create_comments):
    news = News.objects.first()
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == 200
    assert 'news' in response.context
    comments_count = response.context['news'].comment_set.count()
    assert comments_count == 2
    comments = response.context['news'].comment_set.all().order_by('created')
    for i in range(comments_count - 1):
        assert comments[i].created < comments[i + 1].created


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, create_comments):
    news = News.objects.first()
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, create_comments):
    comment = Comment.objects.first()
    author = comment.author
    news = comment.news
    url = reverse('news:detail', args=(news.id,))
    client.force_login(author)
    response = client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], forms.CommentForm)
