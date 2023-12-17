import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model

from news.models import Comment
from news.forms import WARNING
from news.pytest_tests.constans import FORM_DATA, BAD_WORDS_DATA, NEW_FORM_DATA

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, url):
    initial_comments_count = Comment.objects.count()
    response = client.post(url, data=FORM_DATA)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_count == initial_comments_count


@pytest.mark.django_db
def test_user_can_create_comment(auth_client, url):
    initial_comments_count = Comment.objects.count()
    response = auth_client.post(url, data=FORM_DATA)
    comments_count = Comment.objects.count()
    comment = Comment.objects.last()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_count == initial_comments_count + 1
    assert comment.text == FORM_DATA['text']
    assert comment.news == comment.news
    assert comment.author == comment.author


@pytest.mark.django_db
def test_user_cant_use_bad_words(auth_client, url):
    initial_comments_count = Comment.objects.count()
    response = auth_client.post(url, data=BAD_WORDS_DATA)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors['text']
    assert comments_count == initial_comments_count


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, delete_url):
    initial_comments_count = Comment.objects.count()
    response = author_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_count == initial_comments_count - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    comments_count = Comment.objects.count()
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, edit_url):
    response = author_client.post(edit_url, data=NEW_FORM_DATA)
    comment = Comment.objects.last()
    assert response.status_code == HTTPStatus.FOUND
    assert comment.text == NEW_FORM_DATA['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client,
                                                edit_url):
    response = reader_client.post(edit_url, data=NEW_FORM_DATA)
    comment = Comment.objects.last()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text != NEW_FORM_DATA['text']
