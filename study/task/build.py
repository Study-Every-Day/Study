# -*- encoding: utf-8 -*-
# here put the import lib
from . import * # noqa


def build_tasks(tasks):
    """
    Args:
        tasks (list[tuple]):

    Returns:
        merged_tasks (list[Task]): Task instance.
    """
    merged_tasks = []
    for (merged_task_name, task_args) in tasks:
        merged_task = globals().get(merged_task_name)(**task_args)
        merged_tasks.append(merged_task)
    return merged_tasks
