# Application-Local Imports
from ninety_seven_things.lib import enums, role

allow_create_article = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_list_article = role.RoleChecker(allowed_roles=[enums.Role.ANY])
allow_view_article = role.RoleChecker(allowed_roles=[enums.Role.ANY])
allow_view_article_details = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_update_article = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_delete_article = role.RoleChecker(allowed_roles=[enums.Role.APPLICATION_ADMINISTRATOR])
allow_delete_all_article = role.RoleChecker(allowed_roles=[enums.Role.NONE])
