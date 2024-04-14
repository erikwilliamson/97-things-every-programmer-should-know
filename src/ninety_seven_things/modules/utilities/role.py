# Application-Local Imports
from ninety_seven_things.lib import enums, role

# Utilities
allow_reseed_db = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_wipe_db = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
