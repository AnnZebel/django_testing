import pytest
from http import HTTPStatus

from django.contrib.auth import get_user_model
from news.models import Comment
from news.forms import WARNING

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, url, form_data):
    response = client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(auth_client, url, form_data):
    response = auth_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    comment = Comment.objects.get()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_count == 1
    assert comment.text == form_data['text']
    assert comment.news == comment.news
    assert comment.author == comment.author


@pytest.mark.django_db
def test_user_cant_use_bad_words(auth_client, url, bad_words_data):
    response = auth_client.post(url, data=bad_words_data)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.OK
    assert WARNING in response.context['form'].errors['text']
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, delete_url):
    response = author_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    response = reader_client.delete(delete_url)
    comments_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, edit_url, new_form_data):
    response = author_client.post(edit_url, data=new_form_data)
    comment = Comment.objects.get()
    assert response.status_code == HTTPStatus.FOUND
    assert comment.text == new_form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(reader_client,
                                                edit_url, new_form_data):
    response = reader_client.post(edit_url, data=new_form_data)
    comment = Comment.objects.get()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text != new_form_data['text']
