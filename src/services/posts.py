from uuid import uuid4
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.models import User
from src.repository.posts import get_post, get_post_url, add_post


class PostService:

    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )


    async def upload_post(self, file):
        unique_filename = str(uuid4())
        public_id = f"SomeFile/{unique_filename}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(version=r.get("version"))
        return {"public_id": public_id, "url": src_url}


    async def resize_post(self, post_id: str, width: int, height: int, user: User, db: Session):
        post = await get_post(post_id, user=user, db=db)
        transformed_url = cloudinary.uploader.explicit(
            post.public_id,
            type="upload",
            eager=[
                {
                    "width": width,
                    "height": height,
                    "crop": "fill",
                    "gravity": "auto",
                },
                {"fetch_format": "auto"},
                {"radius": "max"},
            ],
        )
        try:
            url_to_return = transformed_url["eager"][0]["secure_url"]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid width or height")
        
        post_in_db = await get_post_url(transformed_url, user, db)
        if post_in_db:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Resource already exists")
        new_post = await add_post(transformed_url, post.public_id, post.description, user, db)
        return url_to_return


    async def add_filter(self, post_id: str, filter: str, user: User, db: Session):
        filters = ["al_dente", "athena", "audrey", "aurora", "daguerre", "eucalyptus", "fes", "frost",
            "hairspray", "hokusai", "incognito", "linen", "peacock", "primavera", "quartz",
            "red_rock", "refresh", "sizzle", "sonnet", "ukulele", "zorro"]
        effect = f"art:{filter}" if filter in filters else filter
        post = await get_post(post_id, user=user, db=db)
        transformed_url = cloudinary.uploader.explicit(
            post.public_id,
            type="upload",
            eager=[{"effect": effect}, {"fetch_format": "auto"}, {"radius": "max"}],
        )
        try:
            url_to_return = transformed_url["eager"][0]["secure_url"]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid filter")
            
        post_in_db = await get_post_url(transformed_url, user, db)
        if post_in_db:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Resource already exists")
        new_post = await add_post(transformed_url, post.public_id, post.description, user, db)
        return url_to_return

post_service = PostService()

post_service = PostService()
