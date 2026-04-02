import math
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


class TestRobotMoves(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node('test_robot_moves')

    def tearDown(self):
        self.node.destroy_node()

    def test_position_changes(self, proc_output):
        positions = []

        def _on_odom(msg):
            p = msg.pose.pose.position
            positions.append((p.x, p.y))

        sub = self.node.create_subscription(Odometry, '/odom', _on_odom, 10)
        try:
            end = time.time() + 90
            while time.time() < end and len(positions) < 50:
                rclpy.spin_once(self.node, timeout_sec=1)

            self.assertGreaterEqual(len(positions), 2,
                                    'Not enough odometry messages received')

            x0, y0 = positions[0]
            x1, y1 = positions[-1]
            dist = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)

            self.assertGreater(
                dist, 0.05,
                f'Robot did not move enough: start=({x0:.4f}, {y0:.4f}), '
                f'end=({x1:.4f}, {y1:.4f}), distance={dist:.4f}m')
        finally:
            self.node.destroy_subscription(sub)


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):
    def test_exit_codes(self, proc_info):
        launch_testing.asserts.assertExitCodes(proc_info)
