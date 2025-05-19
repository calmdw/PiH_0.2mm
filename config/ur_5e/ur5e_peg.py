"""Configuration for the Universal Robots.

The following configuration parameters are available:

* :obj:`UR5e_peg_CFG`: The UR5e arm with a peg.

"""

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.utils.assets import ISAACLAB_NUCLEUS_DIR
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
ur5e_usd_path = os.path.join(script_dir, "ur5e.usd")

##
# Configuration
##


UR5e_PEG_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=ur5e_usd_path,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=True, 
                solver_position_iteration_count=16, 
                solver_velocity_iteration_count=2,
        ),
        activate_contact_sensors=True,
    ),
    # init_state=ArticulationCfg.InitialStateCfg(
    #     joint_pos={
    #         "shoulder_pan_joint": -11 * np.pi/180,
    #         "shoulder_lift_joint": -58 * np.pi/180,
    #         "elbow_joint": 89 * np.pi/180,
    #         "wrist_1_joint": -118 * np.pi/180,
    #         "wrist_2_joint": -90 * np.pi/180,
    #         "wrist_3_joint": 0.0,
    #     },
    # ),
    # bad one
    # init_state=ArticulationCfg.InitialStateCfg(
    #     joint_pos={
    #         "shoulder_pan_joint": 0 * np.pi/180,
    #         "shoulder_lift_joint": -90 * np.pi/180,
    #         "elbow_joint": -90 * np.pi/180,
    #         "wrist_1_joint": -90 * np.pi/180,
    #         "wrist_2_joint": 90 * np.pi/180,
    #         "wrist_3_joint": 0.0,
    #     },
    # ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "shoulder_pan_joint": -15 * np.pi/180,#-15
            "shoulder_lift_joint": -65 * np.pi/180,
            "elbow_joint": 113 * np.pi/180,
            "wrist_1_joint": -138 * np.pi/180,
            "wrist_2_joint": -90 * np.pi/180,
            "wrist_3_joint": -15.0 * np.pi/180,
        },
    ),
    # init_state=ArticulationCfg.InitialStateCfg(
    #     joint_pos={
    #         "shoulder_pan_joint": 0,
    #         "shoulder_lift_joint": -1.57,
    #         "elbow_joint": 1.57,
    #         "wrist_1_joint": -1.57,
    #         "wrist_2_joint": -1.57,
    #         "wrist_3_joint": 0.0,
    #     },
    # ),
    # actuators={
    #     "arm": ImplicitActuatorCfg(
    #         joint_names_expr=[".*"],
    #         velocity_limit_sim=10.0,
    #         effort_limit_sim=66.0,
    #         stiffness=800.0,
    #         damping=120.0,
    #     ),
    # },
    # training
    actuators={
        "arm": ImplicitActuatorCfg(
            joint_names_expr=[".*"],
            velocity_limit_sim=1.0,
            effort_limit_sim=17.0,
            stiffness=1600.0,
            damping=800.0,
        ),
    },

)
"""Configuration of UR-5e arm using implicit actuator models."""