# coding: utf-8

from flask.ext.script import Manager
from flask.ext.security import script as security_script

MANAGER_DESC = "Shelf management commands"

manager = Manager(
    usage = None,
    help = MANAGER_DESC,
    description = MANAGER_DESC,
)
manager.add_command("create_user", security_script.CreateUserCommand())
manager.add_command("activate_user", security_script.ActivateUserCommand())
manager.add_command("deactivate_user", security_script.DeactivateUserCommand())
manager.add_command("create_role", security_script.CreateRoleCommand())
manager.add_command("add_role", security_script.AddRoleCommand())
manager.add_command("remove_role", security_script.RemoveRoleCommand())
