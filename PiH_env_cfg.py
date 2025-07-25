# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import MISSING

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from isaaclab.sim.schemas.schemas_cfg import RigidBodyPropertiesCfg, MassPropertiesCfg
from isaaclab.sim.spawners.from_files.from_files_cfg import UsdFileCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import ActionTermCfg as ActionTerm
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise

import isaaclab_tasks.PiH.mdp as mdp
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
plate_usd_path = os.path.join(script_dir, "plate.usd")

##
# Scene definition
##

@configclass
class PiHSceneCfg(InteractiveSceneCfg):
    """Configuration for the scene with a robotic arm."""

    # world
    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.GroundPlaneCfg(),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -0.05)),
    )

    # base: RigidObjectCfg = RigidObjectCfg(
    #         prim_path="{ENV_REGEX_NS}/Base",
    #         init_state=RigidObjectCfg.InitialStateCfg(pos=[0.65, 0.0, 0.024], rot=[0.707, 0.707, 0, 0]),
    #         spawn=UsdFileCfg(
    #             # usd_path=f"{ISAAC_NUCLEUS_DIR}/Props/Blocks/DexCube/dex_cube_instanceable.usd",
    #             usd_path="/home/xinyu_sim45/Desktop/PiH_assets/mockup_insertion_plate.usd",
    #             scale=(0.001, 0.001, 0.001),
    #             rigid_props=RigidBodyPropertiesCfg(
    #                 solver_position_iteration_count=16,
    #                 solver_velocity_iteration_count=1,
    #                 max_angular_velocity=1e-6,
    #                 max_linear_velocity=0.1,
    #                 max_depenetration_velocity=1e-6,
    #                 disable_gravity=False,
    #             ),
    #         ),
    #     )
    
    base: RigidObjectCfg = RigidObjectCfg(
            prim_path="{ENV_REGEX_NS}/Base",
            # init_state=RigidObjectCfg.InitialStateCfg(pos=[0.55, 0.0, 0.03], rot=[0.707, 0.707, 0, 0]),
            #X90
            init_state=RigidObjectCfg.InitialStateCfg(pos=[0.550, -0.00958, 0.026-0.05], rot=[0.707, 0.707, 0, 0]),
            #X-90_Z-180
            # init_state=RigidObjectCfg.InitialStateCfg(pos=[0.5505, -0.00917, 0.036], rot=[0.0, 0.0, 0.707, 0.707]),
            spawn=UsdFileCfg(
                usd_path=plate_usd_path,
                scale=(1, 1, 1),
                rigid_props=RigidBodyPropertiesCfg(
                    solver_position_iteration_count=4,
                    solver_velocity_iteration_count=1,
                    max_angular_velocity=1e-6,
                    max_linear_velocity=0.1,
                    max_depenetration_velocity=1.0,
                    disable_gravity=False,
                    kinematic_enabled=True,
                ),
            ),
        )

    # contact_forces = ContactSensorCfg(prim_path="{ENV_REGEX_NS}/Robot/tool", history_length=1, track_air_time=True, debug_vis=True)

    # robots
    robot: ArticulationCfg = MISSING

    # lights
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DomeLightCfg(color=(0.75, 0.75, 0.75), intensity=2500.0),
    )


##
# MDP settings
##


@configclass
class CommandsCfg:
    """Command terms for the MDP."""

    ee_pose = mdp.UniformPoseCommandPiHCfg(
        asset_name="robot",
        body_name=MISSING,
        resampling_time_range=(12.0, 12.0),
        debug_vis=True,
        ranges=mdp.UniformPoseCommandPiHCfg.Ranges(
            pos_x=(-0.03, 0, 0.03),
            pos_y=(-0.03, 0, 0.03),
            pos_z=(0.0, 0.0),
            roll=(np.pi * (0/180), np.pi * (0/180)),
            pitch=MISSING,  # depends on end-effector axis
            yaw=(np.pi * (0/180), np.pi * (0/180)),
        ),
    )


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""

    arm_action: ActionTerm = MISSING
    gripper_action: ActionTerm | None = None


@configclass
class ObservationsCfg:
    """Observation specifications for the MDP."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations for policy group."""

        # observation terms (order preserved)
        joint_pos = ObsTerm(func=mdp.joint_pos_rel, noise=Unoise(n_min=-0.01, n_max=0.01))
        # joint_vel = ObsTerm(func=mdp.joint_vel_rel, noise=Unoise(n_min=-0.01, n_max=0.01))
        # pose_distance = ObsTerm(func=mdp.pose_distance, params={"command_name": "ee_pose", "asset_cfg": SceneEntityCfg("robot", body_names="peg")})
        pose_distance = ObsTerm(func=mdp.eef_pose, params={"asset_cfg": SceneEntityCfg("robot", body_names="peg")})
        target_pose = ObsTerm(func=mdp.generated_commands, params={"command_name": "ee_pose"})
        actions = ObsTerm(func=mdp.last_action)
        # contact_force = ObsTerm(func=mdp.contact_force, params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*tool")})

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    # observation groups
    policy: PolicyCfg = PolicyCfg()


@configclass
class EventCfg:
    """Configuration for events."""

    reset_robot_joints = EventTerm(
        func=mdp.reset_joints_by_scale,
        mode="reset",
        params={
            "position_range": (0.9, 1.1),
            "velocity_range": (0.0, 0.0),
        },
    )

    reset_object_position = EventTerm(
        func=mdp.reset_root_state_PiH,
        mode="reset",
        params={
            # for ur5e
            # "pose_range": {"x": (-0.03, 0.03), "y": (-0.03, 0.03), "z": (-0.001, 0.001), "roll": (0.0, 0.0), "yaw": (0.0, 0.0)},
            # "pose_range": {"x": (-0.07, 0.07), "y": (-0.07, 0.07), "z": (-0.001, 0.001), "roll": (0.0, 0.0), "yaw": (0.0, 0.0)},
            # for collecting data
            #0,0, 5mm
            # "pose_range": {"x": (0.0, 0.0), "y": (0.03, 0.03), "z": (0.0, 0.0), "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)},
            # 0,1, 5mm
            # "pose_range": {"x": (0.03, 0.03), "y": (0.0, 0.0), "z": (0.0, 0.0), "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)},
            # 0,2, 5mm
            # "pose_range": {"x": (0.06, 0.06), "y": (0.0, 0.0), "z": (0.0, 0.0), "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)},

            # 1,0, 5mm
            # "pose_range": {"x": (0.0, 0.0), "y": (0.03, 0.03), "z": (0.0, 0.0), "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)},
            # 2,0, 5mm
            # "pose_range": {"x": (0.0, 0.0), "y": (0.06, 0.06), "z": (0.0, 0.0), "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)},

            #-1, 0, 5mm
            # "pose_range": {"x": (0.0, 0.0), "y": (-0.03, -0.03), "z": (0.0, 0.0), "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)},
            #-2, 0, 5mm
            # "pose_range": {"x": (0.0, 0.0), "y": (-0.06, -0.06), "z": (0.0, 0.0), "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)},

            #0, -1, 5mm
            # "pose_range": {"x": (-0.03, -0.03), "y": (0.0, 0.0), "z": (0.0, 0.0), "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)},
            # 0, -2, 5mm
            # "pose_range": {"x": (-0.06, -0.06), "y": (0.0, 0.0), "z": (0.0, 0.0), "roll": (0.0, 0.0), "pitch": (0.0, 0.0), "yaw": (0.0, 0.0)},

            "velocity_range": {}, 
            "asset_cfg": SceneEntityCfg("base", body_names="Base"),
        },
    )


@configclass
class RewardsCfg:
    """Reward terms for the MDP."""
    # action penalty
    action_rate = RewTerm(func=mdp.action_rate_l2, weight=-0.002)

    joint_vel = RewTerm(
        func=mdp.joint_vel_l2,
        weight=-0.001,
        params={"asset_cfg": SceneEntityCfg("robot")},
    )

    end_effector_position_tracking = RewTerm(
        func=mdp.position_command_error,
        weight=-0.6,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=MISSING), "command_name": "ee_pose"},
    )

    end_effector_position_tracking_fine_grained = RewTerm(
        func=mdp.position_command_error_tanh,
        weight=0.3,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=MISSING), "std": 0.1, "command_name": "ee_pose"},
    )

    end_effector_orientation_tracking = RewTerm(
        func=mdp.orientation_command_error,
        weight=-0.9,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=MISSING), "command_name": "ee_pose"},
    )

    ori_distance = RewTerm(
        func=mdp.ori_aligned,
        weight=1.6,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=MISSING), "command_name": "ee_pose"},
    )

    xyz_distance = RewTerm(
        func=mdp.xyz_aligned,
        weight=1.6,
        params={"asset_cfg": SceneEntityCfg("robot", body_names=MISSING), "command_name": "ee_pose"},
    )

    # ori_error = RewTerm(
    #     func=mdp.orientation_command_error,
    #     weight=-0.28,
    #     params={"asset_cfg": SceneEntityCfg("robot", body_names=MISSING), "command_name": "ee_pose"},
    # )

    # xyz_error = RewTerm(
    #     func=mdp.xyz_command_error,
    #     weight=-0.16,
    #     params={"asset_cfg": SceneEntityCfg("robot", body_names=MISSING), "command_name": "ee_pose"},
    # )

    # xyz_error_tanh = RewTerm(
    #     func=mdp.xyz_command_error_tanh,
    #     weight=0.26,
    #     params={"asset_cfg": SceneEntityCfg("robot", body_names=MISSING), "std": 0.1, "command_name": "ee_pose"},
    # )

    # aligned_insert = RewTerm(
    #     func=mdp.z_command_error_tanh,
    #     weight=0.66,
    #     params={"asset_cfg": SceneEntityCfg("robot", body_names=MISSING), "std": 0.1, "command_name": "ee_pose"},
    # )

    # success = RewTerm(
    #     func=mdp.success_reward,
    #     weight=6,
    #     params={"asset_cfg": SceneEntityCfg("robot", body_names="peg"), "command_name": "ee_pose"},
    # )

    # force_penalty = RewTerm(
    #     func=mdp.force_penalty,
    #     weight=-0.001,
    #     params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*tool"), "threshold": 12.0},
    # )


@configclass
class TerminationsCfg:
    """Termination terms for the MDP."""

    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    out_of_workspace = DoneTerm(
        func=mdp.out_of_workspace,
        params={"asset_cfg": SceneEntityCfg("robot", body_names="peg"), "command_name": "ee_pose", "limit_pos": 0.1},
        )

@configclass
class CurriculumCfg:
    """Curriculum terms for the MDP."""

    action_rate = CurrTerm(
        func=mdp.modify_reward_weight, params={"term_name": "action_rate", "weight": -0.02, "num_steps": 4500}
    )

    # joint_vel = CurrTerm(
    #     func=mdp.modify_reward_weight, params={"term_name": "joint_vel", "weight": -0.001, "num_steps": 4500}
    # )

    # force_penalty = CurrTerm(
    #     func=mdp.modify_reward_weight, params={"term_name": "force_penalty", "weight": -0.01, "num_steps": 3500}
    # )

    # force_penalty = CurrTerm(
    #     func=mdp.modify_reward_weight, params={"term_name": "force_penalty", "weight": -0.06, "num_steps": 8500}
    # )


##
# Environment configuration
##


@configclass
class PiHEnvCfg(ManagerBasedRLEnvCfg):
    """Configuration for the reach end-effector pose tracking environment."""

    # Scene settings
    scene: PiHSceneCfg = PiHSceneCfg(num_envs=4096, env_spacing=2.5)
    # Basic settings
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    # MDP settings
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        """Post initialization."""
        # general settings
        self.decimation = 4
        self.sim.render_interval = self.decimation
        # self.sim.render_interval = 1
        self.episode_length_s = 10.0
        self.viewer.eye = (3.5, 3.5, 3.5)
        # simulation settings
        self.sim.dt = 1.0 / 600.0
        # if self.scene.contact_forces is not None:
        #     self.scene.contact_forces.update_period = self.sim.dt
