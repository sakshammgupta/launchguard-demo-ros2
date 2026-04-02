import os
import time
import unittest

import launch
import launch_testing.actions
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

import rclpy
from geometry_msgs.msg import Twist


def generate_test_description():
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('demo_bot'),
                'launch', 'sim.launch.py',
            )
        )
    )
    return (
        launch.LaunchDescription([
            sim_launch,
            launch_testing.actions.ReadyToTest(),
        ]),
        {},
    )


class TestTopicPublished(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_topic_published')

    def tearDown(self):
        self.node.destroy_node()

    def test_cmd_vel_published(self, proc_output):
        msgs = []
        sub = self.node.create_subscription(
            Twist, '/cmd_vel', lambda msg: msgs.append(msg), 10)
        try:
            end = time.time() + 90
            while time.time() < end and len(msgs) < 10:
                rclpy.spin_once(self.node, timeout_sec=1)
            self.assertGreaterEqual(
                len(msgs), 10,
                f'Expected >= 10 /cmd_vel messages, got {len(msgs)}')
        finally:
            self.node.destroy_subscription(sub)


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):
    def test_exit_codes(self, proc_info):
        launch_testing.asserts.assertExitCodes(proc_info)
