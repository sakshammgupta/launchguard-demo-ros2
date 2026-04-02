import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

os.environ['TURTLEBOT3_MODEL'] = 'burger'
os.environ['GAZEBO_MODEL_DATABASE_URI'] = ''


def generate_launch_description():
    pkg_turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    models_dir = os.path.join(pkg_turtlebot3_gazebo, 'models')
    existing = os.environ.get('GAZEBO_MODEL_PATH', '')
    os.environ['GAZEBO_MODEL_PATH'] = ':'.join(
        filter(None, [models_dir, '/usr/share/gazebo-11/models', existing])
    )

    world = os.path.join(
        pkg_turtlebot3_gazebo, 'worlds', 'empty_world.world',
    )

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items(),
    )

    urdf_path = os.path.join(
        pkg_turtlebot3_gazebo, 'urdf', 'turtlebot3_burger.urdf',
    )
    with open(urdf_path, 'r') as f:
        robot_desc = f.read()

    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': True,
        }],
        output='screen',
    )

    sdf_path = os.path.join(
        pkg_turtlebot3_gazebo, 'models', 'turtlebot3_burger', 'model.sdf',
    )
    spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'turtlebot3_burger',
            '-file', sdf_path,
            '-x', '0.0', '-y', '0.0', '-z', '0.01',
        ],
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
