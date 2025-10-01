from pathlib import Path
import sys
import pytest
import pandas as pd

PROJECT_BASE = Path(__file__).parent.parent.parent

dependencies = [
    PROJECT_BASE / 'python' / 'besee_core',
    PROJECT_BASE / 'python' / 'metrics'
]

for dep in dependencies: sys.path.append(str(dep))

from conftest import get_besee_logs_for_scenario_list
from metrics import rms_jerk

CACC_SCENARIOS = [
    'open_straight_road',
    'straight_road_lead_vehicle_ftp'
]
# CACC_SCENARIO_DATA = get_besee_logs_for_scenario_list(CACC_SCENARIOS, suppress_output=True, delete_csv=False)

# CUSTOM CODE - trying to specify custom csv's to sue
from besee_utils import load_loggers_csv
custom_input = {}
# custom_input["1"] = load_loggers_csv(str(PROJECT_BASE / 'python' / 'test' / 'Custom1.csv'))
custom_input["2"] = load_loggers_csv(str(PROJECT_BASE / 'python' / 'test' / 'Custom2.csv'))

@pytest.mark.parametrize('scenario', custom_input.values())
def test_minimum_following_distance_requirement(scenario):
    '''
    requirement under test: at all points in time, the lead vehicle shall not be closer to the 
    ego in the positive x direction than the competition-defined closest following distance from the fdcw
    '''
    
    # load data from metadata dictionary (ignore first 10 entries of csv (0.1sec) to skip setup rows)
    df: pd.DataFrame = scenario['df']
    df = df.iloc[10:]
    scenario_name = scenario['scenario_name']
    
    # IMPLEMENT ME! :) 

    #1.Identify if actor_lead_x exists in the dataframe columns 
    if 'ACTOR_lead_x' not in df.columns: 
        pytest.skip('There is no lead vehicle in this scenario') 
    
    #2.Define ego_position and ego_speed and difference in position 
    ego_x = df['ACTOR_ego_x']
    lead_x = df['ACTOR_lead_x']
    lead_speed = df['ACTOR_lead_speed'] * 2.23694 
    following_distance = lead_x - ego_x

    #3 Defining minimum distance that ego_car can go 
    minimum_distance = 2.8 * (lead_speed ** 0.45) + 8 

    #4 Checking if the requirement is violated at any times 
    test_min_distance_failures = following_distance < minimum_distance
    failure_indices = test_min_distance_failures[test_min_distance_failures].index 
    
    if len(failure_indices) > 0: 
        failure_times = df.loc[failure_indices, 'time'].tolist()
        actual_distance = following_distance[failure_indices] 
        needed_distance = minimum_distance[failure_indices]
        failure_df = pd.DataFrame({
            'time' : failure_times, 
            'distance': actual_distance, 
            'needed_distance': needed_distance
        })
    
        pytest.fail(
            f"Scenario {scenario_name} failed the distance requirement.\n"
            f"{failure_df.to_string(index=False)}")

@pytest.mark.parametrize('scenario', custom_input.values())
def test_speed_error_requirement(scenario):
    '''
    requirement under test: at steady state, the relative speed error must not exceed 10%
    '''
    
    # load data from metadata dictionary (ignore first 10 entries of csv (0.1sec) to skip setup rows)
    df: pd.DataFrame = scenario['df']
    df = df.iloc[10:]
    scenario_name = scenario['scenario_name']
    
    # IMPLEMENT ME! :)

    #0. Defining a "steady state".
    """
    A "steady state" is defined with the following lines of reasoning:
    - A "steady state" should be when acceleration is not changing too much moment to moment
        - This will exclude in the steady state braking, rapidly accelerating 
            (eg from a red light), or other traffic events.
        - This will include in the steady state normal speed adjustment noise when following 
            a car or keeping to a speed limit or other minor things.
    - A "steady state" should not include when brakes are being applied
    - A "steady state" subject to this test should only include when the CAV system is active.
    """

    #1. Defining the relevant data from columns in the dataframe
    ego_acceleration = df["ego_acceleration"]
    ego_braking = df["brake_pos"]
    ego_cav_enable = df["cav_enable"]

    ego_speed = df["ego_speed"]
    ego_target_speed = df["ego_set_speed"]


    #2. Defining relevant thresholds and derived data

    # acceleration_threshold determined by:
    # 1. Assuming 0-60mph takes ~10s
    # 2. Converting 60mph to m/s (26.8224 m/s) and dividing by 10s to get 2.68224 m/s^2
    # 3. Taking roughly 1/4 of that value (to allow for some wiggle room) to get 0.67 m/s^2
    # *Value is currently arbitrary and only based on assumed accelerations of simple driving
    acceleration_threshold = 0.67

    # Defined in the range 0 to 1, 0 for 0% speed error and 1 for 100% speed error.
    relative_speed_error_threshold = 0.1
    relative_speed_error = ((ego_target_speed - ego_speed)/ego_target_speed).abs()

    #3. Filtering for moments that are in the steady state
    
    # Creation of conditions
    valid_acceleration = ego_acceleration.abs() <= acceleration_threshold
    valid_braking = ego_braking == 0
    valid_cav_enable = ego_cav_enable == 1
    steady_state_condition = (valid_acceleration & valid_braking & valid_cav_enable)
    
    exceeding_relative_speed_error_threshold = relative_speed_error > relative_speed_error_threshold
    test_failure_condition = (steady_state_condition & exceeding_relative_speed_error_threshold)

    #4. Checking if condition is invalidated at any time

    # Filter out all rows that match the previous conditions
    failures = df[test_failure_condition]

    if (len(failures)) > 0:

        failure_df = pd.DataFrame({
            "time" : failures["time"], 
            "ego_speed": failures["ego_speed"], 
            "ego_target_speed": failures["ego_set_speed"],
            # "speed_error": failures["speed_error"],
            "relative_speed_error": relative_speed_error[failures.index]
        })
    
        pytest.fail(
            f"Scenario {scenario_name} failed the speed error requirement.\n"
            f"{failure_df.to_string(index=False)}")