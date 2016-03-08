# coding: utf-8

from flask.ext.script import Command, Manager
from flask.ext.security import script as security_scrit

manager = Manager(usage = "Runs Shelf management commands")
manager.add_command("create_user", security_scrit.CreateUserCommand())
manager.add_command("activate_user", security_scrit.ActivateUserCommand())
manager.add_command("deactivate_user", security_scrit.DeactivateUserCommand())
manager.add_command("create_role", security_scrit.CreateRoleCommand())
manager.add_command("add_role", security_scrit.AddRoleCommand())
manager.add_command("remove_role", security_scrit.RemoveRoleCommand())
