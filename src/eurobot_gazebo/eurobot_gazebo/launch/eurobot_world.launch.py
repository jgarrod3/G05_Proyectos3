import os
import tempfile
from glob import glob

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, OpaqueFunction,
                            SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# IDs de ArUco disponibles para el robot (modelos worlds/models/aruco_<ID>)
ROBOT_ARUCO_IDS = [str(i) for i in range(51, 60)]
# La plantilla del robot lleva este ArUco; el launch lo sustituye por el elegido
TEMPLATE_ARUCO = 'aruco_51'

# Equivalente a "export TURTLEBOT3_MODEL=waffle". Si ya está definida en la
# terminal, se respeta ese valor.
os.environ.setdefault('TURTLEBOT3_MODEL', 'waffle')
TURTLEBOT3_MODEL = os.environ['TURTLEBOT3_MODEL']


def spawn_robot(context, models_dir):
    """Crea una copia del robot con el ArUco elegido y la añade a Gazebo."""
    aruco = 'aruco_' + LaunchConfiguration('aruco').perform(context)
    with open(os.path.join(models_dir, 'turtlebot3_waffle_aruco', 'model.sdf')) as f:
        sdf = f.read().replace(TEMPLATE_ARUCO, aruco)
    sdf_file = os.path.join(tempfile.gettempdir(), f'turtlebot3_waffle_{aruco}.sdf')
    with open(sdf_file, 'w') as f:
        f.write(sdf)

    return [Node(
        package='gazebo_ros', executable='spawn_entity.py', output='screen',
        arguments=[
            '-entity', 'turtlebot3_waffle_aruco',
            '-file', sdf_file,
            # z=0.02: las ruedas quedan por encima del suelo Eurobot (superficie en z=0.005)
            '-x', LaunchConfiguration('x').perform(context),
            '-y', LaunchConfiguration('y').perform(context),
            '-z', '0.02',
            '-Y', LaunchConfiguration('yaw').perform(context),
        ],
    )]


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Ruta al world eurobot dentro del paquete
    pkg_eurobot = get_package_share_directory('eurobot_gazebo')
    world = os.path.join(pkg_eurobot, 'worlds', 'eurobot.world')

    # Modelos propios del paquete (valla, aruco_*, turtlebot3_waffle_aruco...).
    # Se anteponen para que tengan prioridad sobre copias en ~/.gazebo/models.
    models_dir = os.path.join(pkg_eurobot, 'worlds', 'models')

    # Modelos que trae Gazebo (sun, ground_plane...). Solo están en GAZEBO_MODEL_PATH
    # si se ha hecho "source /usr/share/gazebo/setup.sh"; si no, Gazebo los descarga
    # de internet cada vez que faltan en ~/.gazebo/models (más de un minuto).
    gazebo_models = sorted(glob('/usr/share/gazebo-*/models'))

    launch_file_dir = os.path.join(
        get_package_share_directory('turtlebot3_gazebo'),
        'launch'
    )

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    return LaunchDescription([
        DeclareLaunchArgument(
            'aruco', default_value='51', choices=ROBOT_ARUCO_IDS,
            description='ID del ArUco (DICT_4X4_100) que lleva el robot encima'),
        # Coordenadas del reglamento Eurobot: origen en la esquina, tablero de 3 x 2 m.
        # Por defecto, el centro del tablero mirando hacia el lado amarillo (x = 0).
        DeclareLaunchArgument('x', default_value='1.5', description='Posición inicial x (m, 0-3)'),
        DeclareLaunchArgument('y', default_value='1.0', description='Posición inicial y (m, 0-2)'),
        DeclareLaunchArgument('yaw', default_value='3.14159',
                              description='Orientación inicial (rad)'),

        *[AppendEnvironmentVariable('GAZEBO_MODEL_PATH', d) for d in gazebo_models],
        AppendEnvironmentVariable('GAZEBO_MODEL_PATH', models_dir, prepend=True),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
            ),
            launch_arguments={'world': world}.items(),
        ),

        # Lanzar la interfaz gráfica
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
            ),
        ),

        # Lanzar el robot_state_publisher
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(launch_file_dir, 'robot_state_publisher.launch.py')
            ),
            launch_arguments={'use_sim_time': use_sim_time}.items(),
        ),

        # Añadir el robot con el ArUco elegido
        OpaqueFunction(function=spawn_robot, args=[models_dir]),
    ])
