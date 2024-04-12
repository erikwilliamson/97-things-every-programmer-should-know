from ninety_seven_things.modules.user import models as user_models
from ninety_seven_things.lib import models

class ApplicationAdministrator(user_models.User, models.Timestamped):
    pass
