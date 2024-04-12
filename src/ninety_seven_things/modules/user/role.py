# Application-Local Imports
from ninety_seven_things.lib import enums
from ninety_seven_things.lib.role import RoleChecker

allow_create_user = RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_create_anonymous_user = RoleChecker(allowed_roles=[enums.Role.ANY])
allow_update_user = RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_delete_user = RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_list_user = RoleChecker(allowed_roles=[enums.Role.ANY])
allow_view_user = RoleChecker(allowed_roles=[enums.Role.ANY])
allow_impersonate_user = RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
