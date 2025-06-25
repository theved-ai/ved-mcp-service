import asyncio
import logging
from typing import Any, Optional
from app.decorators.retry_decorator import async_retryable
from app.webclients.gsuite.gtasks.base import GoogleTasksClientBase
from app.webclients.gsuite.google_service_builder import generate_authenticated_client
from app.utils.constants import google_tasks_service_version, google_tasks_service_name

logger = logging.getLogger(__name__)

class GoogleTasksClientImpl(GoogleTasksClientBase):

    @async_retryable()
    async def list_tasklists(self, user_uuid: str, max_results: Optional[int] = None, page_token: Optional[str] = None) -> Any:
        services = await generate_authenticated_client(user_uuid, google_tasks_service_name, google_tasks_service_version)
        for service in services:
            try:
                req = service.tasklists().list()
                if max_results:
                    req = req.maxResults(max_results)
                if page_token:
                    req = req.pageToken(page_token)
                response = await asyncio.to_thread(req.execute)
                return response.get("items", [])
            except Exception as e:
                logger.error(f"Tasks API error listing tasklists: {e}", exc_info=True)
                raise

    @async_retryable()
    async def get_tasklist(self, user_uuid: str, tasklist_id: str) -> Any:
        services = await generate_authenticated_client(user_uuid, google_tasks_service_name, google_tasks_service_version)
        for service in services:
            try:
                response = await asyncio.to_thread(
                    service.tasklists().get(tasklist=tasklist_id).execute
                )
                return response
            except Exception as e:
                logger.error(f"Tasks API error getting tasklist: {e}", exc_info=True)
                raise

    @async_retryable()
    async def list_tasks(self, user_uuid: str, tasklist_id: str, show_completed: Optional[bool] = None,
                         show_hidden: Optional[bool] = None, show_deleted: Optional[bool] = None,
                         max_results: Optional[int] = None, due_min: Optional[str] = None,
                         due_max: Optional[str] = None, page_token: Optional[str] = None) -> Any:
        services = await generate_authenticated_client(user_uuid, google_tasks_service_name, google_tasks_service_version)
        for service in services:
            try:
                params = {'tasklist': tasklist_id}
                if show_completed is not None:
                    params['showCompleted'] = show_completed
                if show_hidden is not None:
                    params['showHidden'] = show_hidden
                if show_deleted is not None:
                    params['showDeleted'] = show_deleted
                if max_results:
                    params['maxResults'] = max_results
                if due_min:
                    params['dueMin'] = due_min
                if due_max:
                    params['dueMax'] = due_max
                if page_token:
                    params['pageToken'] = page_token

                req = service.tasks().list(**params)
                response = await asyncio.to_thread(req.execute)
                return response.get("items", [])
            except Exception as e:
                logger.error(f"Tasks API error listing tasks: {e}", exc_info=True)
                raise


    @async_retryable()
    async def get_task(self, user_uuid: str, tasklist_id: str, task_id: str) -> Any:
        services = await generate_authenticated_client(user_uuid, google_tasks_service_name, google_tasks_service_version)
        for service in services:
            try:
                response = await asyncio.to_thread(
                    service.tasks().get(tasklist=tasklist_id, task=task_id).execute
                )
                return response
            except Exception as e:
                logger.error(f"Tasks API error getting task: {e}", exc_info=True)
                raise

    @async_retryable()
    async def create_task(self, user_uuid: str, tasklist_id: str, title: str,
                          notes: Optional[str] = None, due: Optional[str] = None,
                          status: Optional[str] = None, parent: Optional[str] = None,
                          previous: Optional[str] = None) -> Any:
        services = await generate_authenticated_client(user_uuid, google_tasks_service_name, google_tasks_service_version)
        body = {"title": title}
        if notes:
            body["notes"] = notes
        if due:
            # Timestamp is ignored even if sent. Limitation by google
            # Ref: https://googleapis.github.io/google-api-python-client/docs/dyn/tasks_v1.tasks.html#insert
            body["due"] = due
        if status:
            body["status"] = status
        if parent:
            body["parent"] = parent
        if previous:
            body["previous"] = previous

        for service in services:
            try:
                response = await asyncio.to_thread(
                    service.tasks().insert(tasklist=tasklist_id, body=body).execute
                )
                return response
            except Exception as e:
                logger.error(f"Tasks API error creating task: {e}", exc_info=True)
                raise

    @async_retryable()
    async def modify_task(self, user_uuid: str, tasklist_id: str, task_id: str,
                          title: Optional[str] = None, notes: Optional[str] = None,
                          due: Optional[str] = None, status: Optional[str] = None,
                          parent: Optional[str] = None, previous: Optional[str] = None,
                          completed: Optional[str] = None, deleted: Optional[bool] = None,
                          hidden: Optional[bool] = None, position: Optional[str] = None) -> Any:
        services = await generate_authenticated_client(user_uuid, google_tasks_service_name, google_tasks_service_version)
        body = {}
        if title:
            body["title"] = title
        if notes:
            body["notes"] = notes
        if due:
            body["due"] = due
        if status:
            body["status"] = status
        if parent:
            body["parent"] = parent
        if previous:
            body["previous"] = previous
        if completed:
            body["completed"] = completed
        if deleted is not None:
            body["deleted"] = deleted
        if hidden is not None:
            body["hidden"] = hidden
        if position:
            body["position"] = position

        for service in services:
            try:
                response = await asyncio.to_thread(
                    service.tasks().patch(tasklist=tasklist_id, task=task_id, body=body).execute
                )
                return response
            except Exception as e:
                logger.error(f"Tasks API error modifying task: {e}", exc_info=True)
                raise

    @async_retryable()
    async def delete_task(self, user_uuid: str, tasklist_id: str, task_id: str) -> Any:
        services = await generate_authenticated_client(user_uuid, google_tasks_service_name, google_tasks_service_version)
        for service in services:
            try:
                await asyncio.to_thread(
                    service.tasks().delete(tasklist=tasklist_id, task=task_id).execute
                )
                return True
            except Exception as e:
                logger.error(f"Tasks API error deleting task: {e}", exc_info=True)
                raise
