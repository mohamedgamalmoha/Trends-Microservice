from typing import Annotated

from celery import uuid
from fastapi import APIRouter, HTTPException, Header, Depends, Query, status
from shared_utils import messages
from shared_utils.schemas.user import User
from shared_utils.exceptions import ObjDoesNotExist
from shared_utils.api.deps.user import get_current_user, get_current_admin_user
from shared_utils.pagination import PageNumberPaginationQueryParams, PageNumberPaginationResponse, PageNumberPaginator

from app.core.security import verify_task_signature
from app.services.task import TaskService, get_task_service
from app.schemas.task import TaskCreate, TaskRetrieve, ThinkTaskUpdate
from app.celery.tasks import think_task


task_router = APIRouter(
    prefix='/think',
    tags=['question']
)


@task_router.post("/task/", response_model=TaskRetrieve)
async def create_task_route(
        task: TaskCreate,
        current_user: User = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service)
    ):
    """
    Create a new task.
    This endpoint allows users to create a new task. The task is created with the provided details.
    The task is then processed asynchronously using a Celery task.

    Args:
        - task (TaskCreate): The task details to create.
        - current_user (User): The current authenticated user.
        - task_service (TaskService): The task service instance.

    Returns:
        - TaskRetrieve: The created task details.

    Raises:
        - HTTPException: If the user is not authorized to create the task.
    """
    if not current_user.is_admin and task.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )
    
    task_id = uuid()

    db_task = await task_service.create(
        id=task_id,
        ** task.model_dump()
    )

    think_task.apply_async(
        kwargs={
            "question": task.question,
            "context": task.context,
            "temperature": task.temperature,
            "max_tokens": task.max_tokens
        },
        task_id=task_id
    )

    return db_task


@task_router.get('/{user_id}/task/{task_id}/', response_model=TaskRetrieve)
async def get_task_route(
        user_id: int,
        task_id: str,
        current_user: User = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service)
    ):
    """
    Get a task by its ID.
    This endpoint allows users to retrieve a task by its ID. The task is fetched from the database.

    Args:
        - user_id (int): The ID of the user who owns the task.
        - task_id (str): The ID of the task to retrieve.
        - current_user (User): The current authenticated user.
        - task_service (TaskService): The task service instance.

    Returns:
        - TaskRetrieve: The task details.

    Raises:
        - HTTPException: If the user is not authorized to access the task or if the task is not found.
    """
    if not current_user.is_admin and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    try:
        db_task = await task_service.get_by_user_id(
            id=task_id,
            user_id=user_id
        )
    except ObjDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.TASK_NOT_FOUND_MESSAGE
        )

    return db_task


@task_router.get("/{user_id}/tasks/", response_model=PageNumberPaginationResponse[TaskRetrieve])
async def get_user_tasks_route(
        user_id: int,
        current_user: User = Depends(get_current_user),
        query_params: Annotated[PageNumberPaginationQueryParams, Query()] = None,
        task_service: TaskService = Depends(get_task_service)
    ):
    """
    Get all tasks for a user.
    This endpoint allows users to retrieve all tasks associated with a specific user ID.

    Args:
        - user_id (int): The ID of the user whose tasks to retrieve.
        - current_user (User): The current authenticated user.
        - query_params (PageNumberPaginationQueryParams): Pagination parameters including page number and size.
        - task_service (TaskService): The task service instance.

    Returns:
        - PageNumberPaginationResponse[TaskRetrieve]: A paginated response containing task` data associated with the user.
    """
    if not current_user.is_admin and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    db_tasks = await task_service.get_paginated(
        paginator=PageNumberPaginator,
        query_params=query_params,
        response_schema=TaskRetrieve,
        user_id=user_id
    )

    return db_tasks


@task_router.get("{user_id}/tasks/{search_task_id}/", response_model=PageNumberPaginationResponse[TaskRetrieve])
async def get_tasks_by_search_task_id_route(
        user_id: int,
        search_task_id: str,
        current_user: User = Depends(get_current_user),
        query_params: Annotated[PageNumberPaginationQueryParams, Query()] = None,
        task_service: TaskService = Depends(get_task_service)
    ):
    """
    Get tasks by search task ID.
    This endpoint allows users to retrieve tasks associated with a specific search task ID.

    Args:
        - user_id (int): The ID of the user whose tasks to retrieve.
        - search_task_id (str): The ID of the search task to filter tasks by.
        - current_user (User): The current authenticated user.
        - query_params (PageNumberPaginationQueryParams): Pagination parameters including page number and size.
        - task_service (TaskService): The task service instance.

    Returns:
        - PageNumberPaginationResponse[TaskRetrieve]: A paginated response containing task` data associated with
          the search task ID.

    Raises:
        - HTTPException: If the user is not authorized to access the tasks or if no tasks are found.
    """
    if not current_user.is_admin and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    try:
        db_tasks = await task_service.get_paginated(
            paginator=PageNumberPaginator,
            query_params=query_params,
            response_schema=TaskRetrieve,
            user_id=user_id,
            search_task_id=search_task_id,
        )
    except ObjDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.SEARCH_TASKS_NOT_FOUND_MESSAGE
        )

    return db_tasks


@task_router.get("/tasks/", response_model=PageNumberPaginationResponse[TaskRetrieve])
async def get_tasks_route(
        current_user: User = Depends(get_current_admin_user),
        query_params: Annotated[PageNumberPaginationQueryParams, Query()] = None,
        task_service: TaskService = Depends(get_task_service)
    ):
    """
    Get all tasks.
    This endpoint allows admin users to retrieve all tasks in the system.

    Args:
        - current_user (User): The current authenticated admin user.
        - query_params (PageNumberPaginationQueryParams): Pagination parameters including page number and size.
        - task_service (TaskService): The task service instance.

    Returns:
        - PageNumberPaginationResponse[TaskRetrieve]: A paginated response containing task` data.
    """
    return await task_service.get_paginated(
        paginator=PageNumberPaginator,
        query_params=query_params,
        response_schema=TaskRetrieve
    )


@task_router.delete("/{user_id}/task/{task_id}/", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_route(
        user_id: int,
        task_id: str,
        current_user: User = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service)
    ):
    """
    Delete a task by its ID.
    This endpoint allows users to delete a task by its ID. The task is removed from the database.

    Args:
        - user_id (int): The ID of the user who owns the task.
        - task_id (str): The ID of the task to delete.
        - current_user (User): The current authenticated user.
        - task_service (TaskService): The task service instance.

    Returns:
        - None: No content is returned on successful deletion.
    """

    if not current_user.is_admin and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.USER_FORBIDDEN_MESSAGE
        )

    try:
        db_task = await task_service.get_by_user_id(
            id=task_id,
            user_id=user_id,
        )
    except ObjDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.TASK_NOT_FOUND_MESSAGE
        )

    await task_service.delete(id=db_task.id)


@task_router.put("/task/{task_id}/callback/", response_model=None, status_code=status.HTTP_204_NO_CONTENT, tags=["callback"])
async def handle_task_callback(
        task_id: str,
        payload: ThinkTaskUpdate,
        x_signature: str = Header(alias="X-Signature"),
        task_service: TaskService = Depends(get_task_service)
    ) -> None:
    """
    Handle task callback.
    
    This endpoint is used to update the status of a task after it has been processed.
    It verifies the signature of the request to ensure it is valid and then updates the task
    in the database with the provided data.
    
    Args:
        - task_id (str): The ID of the task to update.
        - payload (ThinkTaskUpdate): The data to update the task with.
        - x_signature (str): The signature of the request for verification.
        - task_service (TaskService): The task service instance.
    
    Returns:
        - None: No content is returned on successful update.
    
    Raises:
        - HTTPException: If the signature is invalid or if the task is not found.
    """

    if not verify_task_signature(message=task_id, signature=x_signature):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.INVALID_TOKEN_MESSAGE
            )
    
    try:
        # Fetch the task to ensure it exists before updating
        data = payload.model_dump(exclude_unset=True, exclude={"increment_retry_count", })
        await task_service.update(
            id=task_id,
            ** data
        )

        # Increment retry count if specified in the payload
        if payload.increment_retry_count is True:
            await task_service.increment_retry_count(
                id=task_id,
                increment_by=payload.increment_retry_count
            )
            
    except ObjDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.TASK_NOT_FOUND_MESSAGE
        )
