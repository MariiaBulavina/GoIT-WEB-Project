from datetime import datetime
from typing import List

from fastapi import HTTPException, status
import cloudinary.uploader
from sqlalchemy import Column, func, desc
from sqlalchemy.orm import Session

from src.database.models import Post, User, Tag, TransformedPost, PostRating
from src.schemas.comments import CommentByUser
from src.schemas.posts import PostProfile, PostsByFilter
from src.repository import rating as repository_rating


async def add_post(post_url: str, public_id: str, description: str, user: User, db: Session) -> Post:
    """
    Function to add post.

    :param post_url: str: Url of the post
    :param public_id: str: Public id of the post
    :param description: str: Description of the post
    :param user: User: Author of the post
    :param db: Session: Connection session to database
    :return: Post
    """
    post = Post(
        post_url=post_url,
        public_id=public_id,
        description=description,
        user_id=user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    post.tags = []
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return post


async def delete_post(post_id: int, db: Session) -> Post | None:
    """
    Function to delete post.

    :param post_id: int: id of the post
    :param db: Session: Connection session to database
    :return: Post | None
    """
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )
    if post:
        cloudinary.uploader.destroy(post.public_id)
        post.tags = []
        db.delete(post)
        db.commit()
    return post


async def edit_description(post_id: int, description: str, db: Session) -> Post | None:
    """
    Function to edit post description.

    :param post_id: int: id of the post
    :param description: str: Description of the post
    :param db: Session: Connection session to database
    :return: Post | None
    """
    post = (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )
    if post:
        post.description = description
        post.tags = post.tags
        post.updated_at = datetime.now()
        db.commit()
    return post


async def get_my_posts(user: User, db: Session) -> List[Post]:
    """
    Function to get current user's posts.

    :param user: User: Author of the post
    :param db: Session: Connection session to database
    :return: List[Post]
    """
    result =  db.query(Post).filter(Post.user_id == user.id).all()
    return result



async def get_post(post_id: int, db: Session) -> Post | None:
    """
    Function to get post.

    :param post_id: int: id of the post
    :param db: Session: Connection session to database
    :return: Post | None
    """
    return (
        db.query(Post)
        .filter(Post.id == post_id)
        .first()
    )


async def get_post_url(post_id: int, db: Session) -> Column[str] | None:
    """
    Function to get post url.

    :param post_id: int: id of the post
    :param db: Session: Connection session to database
    :return: Column[str] | None: Url of the post 
    """
    result = db.query(Post).filter(Post.id == post_id).first()
    if result is None:
        return None
    
    return result.post_url


async def add_tag_to_post(post: Post, tag: Tag, db: Session) -> Post:
    """
    Function to add tag to post.

    :param post: Post: The post to which the tag is added
    :param tag: Tag: Tag that is added to the post
    :param db: Session: Connection session to database
    :return: Post
    """
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post not found')
    
    if tag in post.tags:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'The tag {tag.tag} has already been added to this post')
    
    if len(post.tags) == 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You cannot add more than 5 tags to one post')

    post.tags.append(tag)
    post.updated_at = datetime.now()
    db.commit()
    db.refresh(post)
    return post 


async def get_post_by_url(post_url: str, db: Session) -> Post | None:
    """
    Function to get post by url.

    :param post_url: str: Url of the post
    :param db: Session: Connection session to database
    :return: Post | None
    """
    result = db.query(Post).filter(Post.post_url == post_url).first()
    if result is None:
        return None
    
    return result


async def get_transformed_post_by_url(transformed_post_url: str, db: Session) -> TransformedPost | None:
    """
    Function to get transformed post by url.

    :param transformed_post_url: str: Url of the transformed post
    :param db: Session: Connection session to database
    :return: Transformed post | None
    """
    result = db.query(TransformedPost).filter(TransformedPost.transformed_post_url == transformed_post_url).first()
    if result is None:
        return None
    
    return result


async def add_transformed_post(transformed_post_url: str, post_id: int, db: Session) -> TransformedPost:
    """
    Function to add transformed post.

    :param transformed_post_url: str: Url of the transformed post
    :param post_id: int: id of the post we are transforming
    :param db: Session: Connection session to database
    :return: TransformedPost
    """
    transformed_post = TransformedPost(
        transformed_post_url=transformed_post_url,
        post_id=post_id,
        created_at=datetime.now(),
    )
    db.add(transformed_post)
    db.commit()
    db.refresh(transformed_post)
    
    return transformed_post


async def get_transformed_post_url(transformed_post_id: int, db: Session) -> Column[str] | None:
    """
    Function to get transformed post url.

    :param transformed_post_id: int: id of the transformed post
    :param db: Session: Connection session to database
    :return: Column[str] | None: Url of the transformed post 
    """
    result = db.query(TransformedPost).filter(TransformedPost.id == transformed_post_id).first()
    if result is None:
        return None
    
    return result.transformed_post_url


async def get_all_posts(
    current_user: User,
    db: Session,
    keyword: str = None,
    tag: str = None,
    min_rating: float = None,
    max_rating: float = None
):
    """
    Search all posts in the database based on the provided filters
    such as keyword, tag, minimum and maximum rating.

    :param current_user: User: The user making the request.
    :param db: Session: Database session.
    :param keyword: str, optional: Keyword to filter posts by description.
    :param tag: str, optional: Tag to filter posts.
    :param min_rating: float, optional: Minimum rating to filter posts.
    :param max_rating: float, optional: Maximum rating to filter posts.
    :return: PostsByFilter: Response containing the list of filtered posts.
    """
    query = db.query(Post)
    
    if keyword:
        query = query.filter(Post.description.ilike(f"%{keyword}%"))
    
    if tag:
        query = query.filter(Post.tags.any(Tag.tag == tag))

    if min_rating is not None or max_rating is not None:
        query = query.join(PostRating, Post.id == PostRating.post_id)

    if min_rating is not None:
        query = query.group_by(Post.id).having(func.avg(PostRating.rating) >= min_rating)

    if max_rating is not None:
        query = query.group_by(Post.id).having(func.avg(PostRating.rating) <= max_rating)

    query = query.order_by(desc(Post.created_at))
    result = query.all()
    posts = []
    
    for post in result:
        tags = []
        comments = []

        for comment in post.comments:
            new_comment = CommentByUser(user_id=comment.user_id, comment=comment.comment_text)
            comments.append(new_comment)

        for tag in post.tags:
            new_tag = tag.tag
            tags.append(new_tag)

        rating = await repository_rating.calculate_average_rating(post.id, db)
        
        new_post = PostProfile(
            id=post.id,
            url=post.post_url,
            description=post.description,
            average_rating=rating,
            tags=tags,
            comments=comments,
        )
        posts.append(new_post)

    all_posts = PostsByFilter(posts=posts)
    return all_posts