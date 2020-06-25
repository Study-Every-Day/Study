# -*- encoding: utf-8 -*-
# here put the import lib
from .task_base import Task
from .article import ArticleTask
from .video import VideoTask
from .build import build_tasks

__all__ = [
    "Task",
    "ArticleTask",
    "VideoTask",
]
