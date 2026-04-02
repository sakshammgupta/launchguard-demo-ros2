# LaunchGuard Demo — ROS 2 + Gazebo

A self-contained ROS 2 Humble repo for validating the full LaunchGuard pipeline. Uses TurtleBot3 in Gazebo with `launch_testing` to produce deterministic pass/fail results.

## Tests

| Test | What it checks |
|------|---------------|
| `test_topic_published` | `/cmd_vel` topic is being published |
| `test_robot_moves` | Robot position changes in Gazebo |
| `test_speed_threshold` | Robot speed exceeds `MIN_SPEED` constant |

## Local Testing

```bash
source /opt/ros/humble/setup.bash
sudo apt install ros-humble-turtlebot3-gazebo ros-humble-turtlebot3-description

mkdir -p ~/demo_ws/src && cd ~/demo_ws/src
git clone <this-repo> launchguard-demo-ros2
cd ~/demo_ws
colcon build --packages-select demo_bot
colcon test --packages-select demo_bot --return-code-on-test-failure
colcon test-result --verbose
```

## Demo a Regression

1. Connect in LaunchGuard, trigger a run — all 3 tests pass
2. Change `MIN_SPEED = 0.1` to `MIN_SPEED = 999.0` in `src/demo_bot/test/test_speed_threshold.py`
3. Push and trigger — `test_speed_threshold` fails, dashboard shows regression
4. Revert and trigger again — regression clears
