# Standard Library Imports
import logging
from typing import Dict, List

# 3rd-Party Imports
from beanie import PydanticObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from pydantic import ValidationError

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import enums, exceptions, schemas

# Local Folder Imports
from .dependencies import ArticleDependency
from .exceptions import ArticleException, ArticleDoesNotExistException
from .models import Article
from .schemas import (
    ArticleCreate, ArticleUpdate, AbridgedArticleView, FullArticleView
)
from .service import (
    add_vip,
    create,
    delete_all,
    delete_one,
    get_many,
    get_vip_list,
    remove_vip,
    retrieve_clients,
    update,
)

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)

@router.post(
    path="/article",
    status_code=status.HTTP_201_CREATED,
    summary="Create an Article",
)
async def create_article(
    article_in: ArticleCreate,
) -> FullArticleView:
    logger.info(f"Creating article: {article_in.name}")

    try:
        created_article = await create(article_in=article_in, background_tasks=background_tasks)
    except ArticleException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    logger.info(f"Article {article_in.name} created with ID {created_article.id}")

    return FullArticleView(**created_article.dict())


@router.get(
    path="/article",
    status_code=status.HTTP_200_OK,
    summary="Retrieve all Articles",
)
async def read_all_articles(
    skip: int = 0,
    limit: int = 100,
) -> List[FullArticleView]:
    try:
        articles = await get_many(fetch_links=True, skip=skip, limit=limit)
    except ValidationError as exc:
        raise exceptions.DataIntegrityException(source_exception=exc) from exc

    return [FullArticleView(**article.dict()) for article in articles]


@router.get(
    path="/article/{article_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve one Article",
)
async def read_one_article(
    article: ArticleDependency,
) -> FullArticleView:
    return SingleArticleResponse(
        meta=schemas.ResponseMetaData(roles=get_entity_privileges(user_roles=user_roles, articles=[article])),
        data=get_single_article_view(user_roles=user_roles, article=article),
    )


@router.get(
    path="/article/{article_id}/clients",
    dependencies=[Depends(allow_view_article)],
    summary="Retrieve Article's Clients",
)
# async def get_clients(article: ArticleDependency) -> List[user_schemas.UserView]:
async def get_clients(article: ArticleDependency) -> Response:
    try:
        clients = await retrieve_clients(article_id=article.id)
    except stripe_account_exceptions.StripeAccountException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    # 3rd-Party Imports
    from icecream import ic

    ic(clients)
    return Response(status_code=status.HTTP_200_OK)


@router.patch(
    path="/article/{article_id}",
    dependencies=[Depends(allow_update_article)],
    summary="Update a Article",
)
async def update_article(
    user_roles: user_dependencies.UserRoleDependency,
    article: ArticleDependency,
    updated_article_in: ArticleUpdate,
    background_tasks: BackgroundTasks,
) -> SingleArticleResponse:
    logger.info(f"Updating article {article.name}")

    try:
        updated_article = await update(
            article=article,
            updated_article_in=updated_article_in,
            background_tasks=background_tasks,
        )
    except ArticleException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    return SingleArticleResponse(
        meta=schemas.ResponseMetaData(roles=get_entity_privileges(user_roles=user_roles, articles=[article])),
        data=get_single_article_view(user_roles=user_roles, article=updated_article),
    )


@router.delete(
    path="/article/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(allow_delete_article)],
    summary="Delete a Article",
)
async def delete_one_article(
    article: ArticleDependency, user: user_models.User = Depends(security.current_active_user)
):
    logger.info(f"Deleting article ({article.id}) {article.name} initiated by {user.email}")
    await delete_one(article=article)


@router.delete(
    path="/article",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(allow_delete_all_article)],
    summary="Delete all Articles",
)
async def delete_all_articles(user: user_models.User = Depends(security.current_active_user)):
    logger.info(f"Deleting all articles initiated by {user.email}")
    await delete_all()
    return


@router.post(
    path="/article/{article_id}/vip",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_update_article)],
    summary="Add a VIP to a article",
)
async def create_vip(article: ArticleDependency, vip_in: VIPAdd) -> VIPView:
    logger.info(f"Adding {vip_in.user_id} as a VIP to article {article.name}")

    try:
        created_vip = await add_vip(article_id=article.id, vip_in=vip_in)
    except (
        ArticleDoesNotExistException,
        user_exceptions.UserDoesNotExistException,
        VIPExistsException,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    return VIPView(**created_vip.dict())


@router.get(
    path="/article/{article_id}/vip",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_update_article)],
    summary="View a article's VIPs",
)
async def read_vips(article: ArticleDependency) -> VIPListView:
    vip_list = await get_vip_list(article_id=article.id)

    return VIPListView(
        article=AbridgedArticleView(id=article.id, name=article.name),
        vips=[VIPView(**v.dict()) for v in vip_list.vips],
    )


@router.delete(
    path="/article/{article_id}/vip/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(allow_update_article)],
    summary="Removes a VIP from a article",
    response_class=Response,
)
async def delete_vip(article: ArticleDependency, user: user_dependencies.UserIDDependency):
    logger.info(f"Removing {user.email} as a VIP from article {article.name}")

    await remove_vip(article_id=article.id, user_id=user.id)
    return None
