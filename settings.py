import pathlib

# COVID-19 Variables
# TODO: need to verify these
RECOVERY_RATE_STAGE_0 = 0.5                           # Base chance of recovering from stage 0 (else go to stage 1)
RECOVERY_RATE_STAGE_1 = 0.3                           # Base chance of recovering from stage 1 (else go to stage 2)
RECOVERY_RATE_STAGE_2 = 0.5                           # Base chance of recovering from stage 2 (else go to stage 3)
RECOVERY_RATE_STAGE_3 = 0.9                           # Base chance of recovering from stage 3 (else you die)

CHANGE_OF_GETTING_SICK_FROM_INTERACTION = 0.0000025    # Chance of getting sick from a single interaction)


# Constants
SCHOOL_ID = 0
HOSPITAL_ID = 1
FRONTLINE_ID = 2
NO_WORK_ID = -1


# Other settings
output_dir = pathlib.Path(r'./output')
