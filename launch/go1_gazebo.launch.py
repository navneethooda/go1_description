#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from time import sleep
import filecmp

package_name = 'go1_description'
world_file = 'empty.world'

import xacro

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    paused = LaunchConfiguration('paused', default='true')
    
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_simulation = get_package_share_directory(package_name)

    robot_description_path =  os.path.join(
        pkg_simulation,
        "urdf",
        "go1.urdf",
    )

    with open(robot_description_path, 'r') as infp:
        robot_desc = infp.read()

    controller_config = os.path.join(
        pkg_simulation,
        "config",
        "robot_control.yaml",
    )
    
    robot_description = {"robot_description": robot_desc}
    
    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )
    
    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-topic", "robot_description", "-entity", "go1_description"],
        output="screen",
    )

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[robot_description],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    spawn_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_group_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    return LaunchDescription([
      gazebo,     
      robot_state_publisher_node,
      spawn_entity,
      joint_state_broadcaster_spawner,
      spawn_controller,
    ])