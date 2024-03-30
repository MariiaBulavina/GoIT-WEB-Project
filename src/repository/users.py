from datetime import datetime

from libgravatar import Gravatar
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import select, func

from src.database.models import User, UserRole, Post, Comment, BlacklistToken
from src.schemas.users import UserModel, UserProfile


async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user associated with that email. If no such user exists,
    it will return None.

    :param email: str: Email of the user we want to get
    :param db: Session: Connection to the database
    :return: The first user found in the database that matches the given email
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:

    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Information to create a user
    :param db: Session: Connection to the database
    :return: A user object
    """
    avatar = None

    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)

    check_users_exist = db.query(User).first()
        
    new_user = User(**body.model_dump(), avatar=avatar)

    if not check_users_exist:
        new_user.user_role = UserRole.admin

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the token for a user.

    :param user: User: User for whom the token needs to be updated
    :param token: str | None: The refreshed token
    :param db: Session: Connection to the database
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.

    :param email: str: Email of the user we want to confirm
    :param db: Session: Connection to the database
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar_url(email: str, url: str | None, db: Session) -> User:
    """
    The update_avatar_url function updates the avatar url of a user.

    :param email: str: Email of the user whose avatar needs to be changed
    :param url: str | None: New avatar url
    :param db: Session: Connection to the database
    :return: The updated user
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def get_user_by_username(username: str, db: Session) -> User | None:
    """
    Function to get user by username.

    :param username: str: Name of user
    :param db: Session: Connection session to database
    :return: User or None
    """
    try:
        user = db.query(User).filter(User.username == username).first()
        return user
    except NoResultFound:
        return None
    

async def get_user_by_id(user_id: int, db: Session) -> User | None:
    """
    Function to get user by id.

    :param user_id: int: User id
    :param db: Session: Connection session to database
    :return: User or None
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except NoResultFound:
        return None


async def change_role(email: str, role: UserRole, db: Session) -> User | None:
    """
    Function to change role.

    :param email: str: Email
    :param role: UserRole: Role of user
    :param db: Session: Connection session to database
    :return: User or None
    """
    user = await get_user_by_email(email, db)
    if user:
        user.user_role = role
        db.commit()
        return user
    return None


async def ban_user(email: str, db: Session) -> User | None:
    """
    Function to ban user.

    :param email: str: Email
    :param db: Session: Connection session to database
    :return: User or None
    """
    user = await get_user_by_email(email, db)
    if user:
        user.is_active = False
        db.commit()
        return user
    return None
        

async def unban_user(email: str, db: Session) -> User | None:
    """
    Function to unban user.

    :param email: str: Email
    :param db: Session: Connection session to database
    :return: User or None
    """
    user = await get_user_by_email(email, db)
    if user:
        user.is_active = True
        db.commit()
        return user
    return None


async def get_user_profile(user: User, db: Session) -> UserProfile | None:
    """
    Function to get user profile.

    :param user: User: User
    :param db: Session: Connection session to database
    :return: User profile or None
    """
    if user:
        find_posts = select(func.count()).where(Post.user_id == user.id) 
        posts_number = db.execute(find_posts).scalar()

        find_comments = select(func.count()).where(Comment.user_id == user.id) 
        comments_number = db.execute(find_comments).scalar()
        
        user_profile = UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            confirmed=user.confirmed,
            avatar=user.avatar,
            user_role=user.user_role,
            is_active=user.is_active,
            posts_number=posts_number,
            comments_number=comments_number,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        return user_profile
    
    return None


async def add_to_blacklist(token: str, db: Session) -> None:
    """
    Add a token to the blacklist.

    :param token: str: The JWT that is being blacklisted.
    :param db: Session: SQLAlchemy session object for accessing the database
    return: None
    """
    blacklist_token = BlacklistToken(token=token, added_on=datetime.now())
    db.add(blacklist_token)
    db.commit()
    db.refresh(blacklist_token)
    return None


async def is_blacklisted_token(token: str, db: Session) -> bool:
    """
    Check if a token is blacklisted.

    :param token: str: The JWT that is being blacklisted.
    :param db: Session: SQLAlchemy session object for accessing the database
    return: bool
    """
    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    if blacklist_token:
        return True
    return False
    
