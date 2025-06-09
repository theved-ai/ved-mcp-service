from abc import ABC, abstractmethod
from typing import Optional, Any

class GoogleTasksClientBase(ABC):
    @abstractmethod
    async def list_tasklists(self, user_uuid: str, max_results: Optional[int] = None, page_token: Optional[str] = None) -> Any:
        """
        Lists all task lists for the authenticated user.
        """
        pass

    @abstractmethod
    async def get_tasklist(self, user_uuid: str, tasklist_id: str) -> Any:
        """
        Gets a single task list by ID.
        """
        pass

    @abstractmethod
    async def list_tasks(self, user_uuid: str, tasklist_id: str, show_completed: Optional[bool] = None,
                         show_hidden: Optional[bool] = None, show_deleted: Optional[bool] = None,
                         max_results: Optional[int] = None, due_min: Optional[str] = None,
                         due_max: Optional[str] = None, page_token: Optional[str] = None) -> Any:
        """
        Lists all tasks in the specified task list.
        """
        pass

    @abstractmethod
    async def get_task(self, user_uuid: str, tasklist_id: str, task_id: str) -> Any:
        """
        Gets a single task by ID from the specified task list.
        """
        pass

    @abstractmethod
    async def create_task(self, user_uuid: str, tasklist_id: str, title: str,
                          notes: Optional[str] = None, due: Optional[str] = None,
                          status: Optional[str] = None, parent: Optional[str] = None,
                          previous: Optional[str] = None) -> Any:
        """
        Creates a new task in the specified task list.
        """
        pass

    @abstractmethod
    async def modify_task(self, user_uuid: str, tasklist_id: str, task_id: str,
                          title: Optional[str] = None, notes: Optional[str] = None,
                          due: Optional[str] = None, status: Optional[str] = None,
                          parent: Optional[str] = None, previous: Optional[str] = None,
                          completed: Optional[str] = None, deleted: Optional[bool] = None,
                          hidden: Optional[bool] = None, position: Optional[str] = None) -> Any:
        """
        Updates an existing task in the specified task list.
        """
        pass

    @abstractmethod
    async def delete_task(self, user_uuid: str, tasklist_id: str, task_id: str) -> Any:
        """
        Deletes a task from the specified task list.
        """
        pass
