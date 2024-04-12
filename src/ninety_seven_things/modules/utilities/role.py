# Application-Local Imports
from ninety_seven_things.lib import enums

# Utilities
allow_reseed_db = RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_wipe_db = RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
