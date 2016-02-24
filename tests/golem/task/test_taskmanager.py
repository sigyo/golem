from mock import Mock

from golem.tools.testdirfixture import TestDirFixture
from golem.tools.assertlogs import LogTestCase
from golem.task.taskmanager import TaskManager, logger
from golem.network.p2p.node import Node


class TestTaskManager(LogTestCase, TestDirFixture):

    def test_get_next_subtask(self):
        tm = TaskManager("ABC", Node(), root_path=self.path)
        self.assertIsInstance(tm, TaskManager)

        subtask, wrong_task = tm.get_next_subtask("DEF", "DEF", "xyz", 1000, 5, 10, 2, "10.10.10.10")
        self.assertEqual(subtask, None)
        self.assertEqual(wrong_task, True)
        task_mock = Mock()
        task_mock.header.task_id = "xyz"
        task_mock.header.resource_size = 2 * 1024
        task_mock.header.estimated_memory = 3 * 1024
        task_mock.query_extra_data.return_value.task_id = "xyz"
        tm.add_new_task(task_mock)
        subtask, wrong_task = tm.get_next_subtask("DEF", "DEF", "xyz", 1000, 5, 10, 2, "10.10.10.10")
        self.assertIsNone(subtask)
        self.assertEqual(wrong_task, False)
        tm.tasks_states["xyz"].status = tm.activeStatus[0]
        subtask, wrong_task = tm.get_next_subtask("DEF", "DEF", "xyz", 1000, 1, 10, 2, "10.10.10.10")
        self.assertIsNone(subtask)
        self.assertEqual(wrong_task, False)
        subtask, wrong_task = tm.get_next_subtask("DEF", "DEF", "xyz", 1000, 5, 2, 2, "10.10.10.10")
        self.assertIsNone(subtask)
        self.assertEqual(wrong_task, False)
        subtask, wrong_task = tm.get_next_subtask("DEF", "DEF", "xyz", 1000, 5, 10, 2, "10.10.10.10")
        self.assertIsInstance(subtask, Mock)
        self.assertEqual(wrong_task, False)

    def test_set_value(self):
        tm = TaskManager("ABC", Node(), root_path=self.path)
        with self.assertLogs(logger, level=1) as l:
            tm.set_value("xyz", "xxyyzz", 13)
        self.assertTrue(any(["not my task" in log for log in l.output]))

        task_mock = Mock()
        task_mock.header.task_id = "xyz"
        task_mock.header.resource_size = 2 * 1024
        task_mock.header.estimated_memory = 3 * 1024
        task_mock.query_extra_data.return_value.task_id = "xyz"
        task_mock.query_extra_data.return_value.subtask_id = "xxyyzz"
        tm.add_new_task(task_mock)
        with self.assertLogs(logger, level=1) as l:
            tm.set_value("xyz", "xxyyzz", 13)
        self.assertTrue(any(["not my subtask" in log for log in l.output]))

        tm.tasks_states["xyz"].status = tm.activeStatus[0]
        subtask, wrong_task = tm.get_next_subtask("DEF", "DEF", "xyz", 1000, 5, 10, 2, "10.10.10.10")
        self.assertIsInstance(subtask, Mock)
        self.assertEqual(wrong_task, False)
        tm.set_value("xyz", "xxyyzz", 13)
        self.assertEqual(tm.tasks_states["xyz"].subtask_states["xxyyzz"].value, 13)