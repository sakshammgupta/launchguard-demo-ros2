import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node

os.environ['TURTLEBOT3_MODEL'] = 'burger'
os.environ['GAZEBO_MODEL_DATABASE_URI'] = ''


def generate_launch_description():
    world = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'),
        'worlds', 'empty_world.world',
    )

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch', 'gzserver.launch.py',
            )
        ),
        launch_arguments={'world': world}.items(),
    )

    urdf_file = os.path.join(
        get_package_share_directory('turtlebot3_description'),
        'urdf', 'turtlebot3_burger.urdf.xacro',
    )
    robot_desc = Command(['xacro', urdf_file])

    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True,
        }],
        output='screen',
    )

    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'turtlebot3_burger', '-topic', '/robot_description'],
        output='screen',
    )

    mover = Node(
        package='demo_bot',
        executable='mover.py',
        name='mover',
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        gzserver,
        robot_state_pub,
        spawn,
        mover,
    ])
