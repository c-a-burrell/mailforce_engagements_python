from mailforce.models.message.message_roles import MessageRoles

MESSAGE_ROLES_HEADER: str = 'account,message_id,email_address,role'


class MessageRolesContainer:
    """ Hold multiple message roles. """

    def __init__(self, message_roles: list[MessageRoles]):
        """
        :param message_roles: Message Roles list.
        """
        self.message_roles = message_roles

    def to_csv_rows(self) -> list[str]:
        """
        :return: CSV representation of all the message roles.
        """
        all_roles: list[str] = []
        for message_role in self.message_roles:
            all_roles += message_role.to_csv_rows()
        return [f'{MESSAGE_ROLES_HEADER}\n'] + all_roles
