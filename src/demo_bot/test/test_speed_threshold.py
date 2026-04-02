import os
import time
import unittest

import launch
import launch_testing.actions
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

import rclpy
from nav_msgs.msg import Odometry

MIN_SPEED = 0.1


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
            TimerAction(period=60.0, actions=[launch_testing.actions.ReadyToTest()]),
        ]),
        {},
    )


class TestSpeedThreshold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_speed_threshold')

    def tearDown(self):
        self.node.destroy_node()

    def test_speed_exceeds_minimum(self, proc_output):
        speeds = []

        def _on_odom(msg):
            speeds.append(abs(msg.twist.twist.linear.x))

        sub = self.node.create_subscription(Odometry, '/odom', _on_odom, 10)
        try:
            end = time.time() + 90
            while time.time() < end and len(speeds) < 50:
                rclpy.spin_once(self.node, timeout_sec=1)

            self.assertGreater(len(speeds), 0, 'No odometry messages received')

            max_speed = max(speeds)
            self.assertGreater(
                max_speed, MIN_SPEED,
                f'Max speed {max_speed:.4f} m/s did not exceed '
                f'MIN_SPEED={MIN_SPEED} m/s')
        finally:
            self.node.destroy_subscription(sub)


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):
    def test_exit_codes(self, proc_info):
        launch_testing.asserts.assertExitCodes(proc_info)
