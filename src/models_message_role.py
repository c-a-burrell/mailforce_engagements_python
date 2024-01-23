from domain_utils import is_valid_domain
from hash_utils import deterministic_id

MESSAGE_ROLES_HEADER: str = 'account,message_id,email_address,role'


class MessageRole:
    """ Holds the relationships between a given message Id in a specified account and an email address. """
    def __init__(self, account: str, message_id: str, email_address: str, role: str):
        """
        :param account: Name of the account.
        :param message_id:  Id of the email message.
        :param email_address: Email address.
        :param role: Relationship between the given email address and the message Id, namely whether it originated,
        directly received or was a CC recipient of the email.
        """
        self.account: str = account
        self.message_id: str = message_id
        self.email_address: str = email_address
        self.role: str = role
        self.domain: str = self.email_address.split('@')[1]

    def to_csv_row(self):
        """
        :return: CSV representation of this object.
        """
        return f'{self.account},{self.message_id},{self.email_address},{self.role}'


class MessageRoles:
    """ Holds multiple message - email relationships for a given account. """
    def __init__(self, message_role_json: dict[str, any]):
        """
        :param message_role_json: JSON representing multiple message role mappings for a given account.
        """
        def _message_roles(addresses, role):
            def _message_role(email_address: str):
                return MessageRole(self.account, self.message_id, email_address, role)

            return list(map(_message_role, addresses))

        self.account = message_role_json['account'][0]
        self.message_id = message_role_json['messageId'][0]
        from_addresses = message_role_json['from.address']
        to_addresses = message_role_json['to.address']
        message_roles: list[MessageRole] = _message_roles(from_addresses, 'from')
        message_roles += _message_roles(to_addresses, 'to')
        if 'cc.address' in message_role_json:
            cc_addresses = message_role_json['cc.address']
            message_roles += _message_roles(cc_addresses, 'cc')
        self.roles: list[MessageRole] = list(filter(lambda role: is_valid_domain(role.domain), message_roles))
        all_email_addresses: str = '+'.join(sorted(list(map(lambda message_role: message_role.email_address, self.roles))))
        self.id = deterministic_id(self.account, self.message_id, all_email_addresses)

    def to_csv_rows(self) -> list[str]:
        """
        :return: CSV representation of this instance.
        """
        all_roles = map(lambda message_role: f'{message_role.to_csv_row()}\n', self.roles)
        return list(all_roles)


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
