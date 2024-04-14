# Application-Local Imports
from ninety_seven_things.lib import enums, role

allow_create_author = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_list_author = role.RoleChecker(allowed_roles=[enums.Role.ANY])
allow_view_author = role.RoleChecker(allowed_roles=[enums.Role.ANY])
allow_view_author_details = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_update_author = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_delete_author = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_delete_all_author = role.RoleChecker(allowed_roles=[enums.Role.NONE])
