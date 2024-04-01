from pytest import fixture

from src.database.models import User, UserRole, Post, PostRating
from fastapi import status
import datetime


@fixture(scope='module')
def token(client, user, session):
    response = client.post("/api/auth/signup",
                           json={"username": "deadpool",
                                 "email": "deadpool@example.com",
                                 "password": "123456789"})
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.role = UserRole.admin
    session.commit()
    response = client.post("/api/auth/login",
                           data={"email": "deadpool@example.com", "password": "123456789"},
                           headers={'Content-Type': 'application/x-www-form-urlencoded'})
    data = response.json()
    return data["access_token"]


@fixture(scope='module')
def post(client, user, session):
    response = client.post("/api/auth/signup",
                           json={"username": "deadpool",
                                 "email": "deadpool@example.com",
                                 "password": "123456789"})
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    post = session.query(Post).filter(Post.id == 1).first()
    if post is None:
        post = Post(
            id=1,
            post_url="https://res.cloudinary.com/dy9mhswnt/image/upload/c_fill,g_faces,h_500,r_max,w_500\
                      /v1/photoshare/473db2aa2c097073b2e971767d76f543960ce141f4acf4671e82369de8526e9e",
            user_id=1,
            created_at=datetime.datetime.now(),
            description="test_post",
        )
        session.add(post)
        session.commit()
        session.refresh(post)
    return post


@fixture(scope='module')
def rating(client, user, session):
    response = client.post("/api/auth/signup",
                           json={"username": "deadpool",
                                 "email": "deadpool@example.com",
                                 "password": "123456789"})
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    rating = session.query(Post).filter(PostRating.id == 1).first()
    if rating is None:
        rating = PostRating(
            id=1,
            rating=5,
            user_id=current_user.id,
            post_id=1,
        )
        session.add(rating)
        session.commit()
        session.refresh(rating)
    return rating


def test_create_rating(client, token, post, session):
    response = client.post("/api/rating/1/rating", headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == status.HTTP_200_OK


def test_get_post_rating(client, token, post, session):
    response = client.get("/api/rating/1/rating", headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == status.HTTP_200_OK


def test_delete_rating(client, token, session, rating):
    response = client.delete("/api/rating/1/rating", headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_user_ratings(client, token, post, session):
    response = client.get("/api/rating/users/1/rating", headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == status.HTTP_200_OK
