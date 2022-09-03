"""

- CSH User Tool 'tool.py' Source Code -

(C) Cubeflix 2022 (CSH)

"""


# ---------- IMPORTS ----------

from .misc import *
from .auth import *


# ---------- CLASSES ----------

class UserTool:

        """The main CSH user tool class."""

        def __init__(self, file):

            """Create the CSH user tool.
               Args: file -> The users file to use and manage."""

            self.file = file

            # Set up and open the file
            self._setup()

        def _setup(self):
            
            """Set up and open the users file."""

            file_handler = open(self.file)

            # Use JSON to read and parse it
            try:
                self.data = json.load(file_handler)
            
            except Exception as e:
                # Error with parsing JSON data
                print("ERROR WITH PARSING FILE: [" + str(e) + "]")

            finally:
                # Close the file handle
                file_handler.close()

        def _save(self):

            """Save the data into the file."""

            file_handler = open(self.file, 'w')

            # Use JSON to dump it
            try:
                json.dump(self.data, file_handler)

            except Exception as e:
                # Error with dumping JSON data
                print("ERROR WITH SAVING FILE: [" + str(e) + "]")

            finally:
                # Close the file handler
                file_handler.close()

        def create_user(self, username, password, permissions):

            """Create a user in the users file.
               Args: username -> The username for the new user.
                     password -> The password for the new user.
                     permissions -> The permissions for the new user. Can be 'r', 'w', or 'a', for reading, writing, and administrative privileges, respectively."""

            if not permissions in ('r', 'w', 'a'):
                # Throw an error
                raise UserToolError("Permissions must be either 'r', 'w', or 'a'.")

            # Create the new user
            user = {"username": username, "password_hash": hash_password(password), "permissions": permissions}

            # Add the user
            self.data[username] = user

            # Save the file
            self._save()

        def delete_user(self, username):

            """Delete a user in the users file.
               Args: username -> The username of the user to delete."""

            if not username in self.data:
                # Throw an error
                raise UserToolError("User does not exist.")

            # Delete the user
            del self.data[username]

            # Save the file
            self._save()

        def get_user(self, username):

            """Get the password hash and permissions for a user.
               Args: username -> The username of the user to get information on."""

            if not username in self.data:
                # Throw an error
                raise UserToolError("User does not exist.")

            # Get the user data
            return self.data[username]

        def edit_user(self, username, password=None, permissions=None):

            """Edit the user data for a user.
               Args: username -> The username of the user to update.
                     password -> If the password should change, this should be the new password.
                     permissions -> If the permissions should change, this should be the new permissions."""

            if not username in self.data:
                # Throw an error
                raise UserToolError("User does not exist.")

            # Check for password update
            if password:
                # Change the password
                self.data[username]["password_hash"] = hash_password(password)

            # Check for permissions update
            if permissions:
                # Check that the permissions are valid
                if not permissions in ('r', 'w', 'a'):
                    # Throw an error
                    raise UserToolError("Permissions must be either 'r', 'w', or 'a'.")

                # Change the permissions
                self.data[username]["permissions"] = permissions

            # Save the file
            self._save()
