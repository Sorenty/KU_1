import os
import tarfile
import xml.etree.ElementTree as ET
from datetime import datetime
import argparse


class ShellEmulator:
    def __init__(self, tar_path, log_path):
        self.tar_path = tar_path
        self.log_path = log_path
        self.fs = {}  # In-memory representation of the virtual file system
        self.current_path = "/"
        self.log_actions = []  # To store actions for the session
        self.current_user = self.request_login()  # Set current user at startup
        self.load_tar()

    def request_login(self):
        """Requests the user to log in at the start of the session."""
        user = input("Enter your username: ").strip()
        if not user:
            print("Username cannot be empty. Using 'guest' as default.")
            return "guest"
        return user

    def load_tar(self):
        """Loads the tar archive into an in-memory file system representation."""
        if not tarfile.is_tarfile(self.tar_path):
            raise ValueError(f"{self.tar_path} is not a valid tar file.")
        with tarfile.open(self.tar_path, "r") as tar:
            for member in tar.getmembers():
                parts = member.name.split("/")
                node = self.fs
                for part in parts[:-1]:
                    node = node.setdefault(part, {})
                if member.isfile():
                    node[parts[-1]] = {"type": "file", "content": tar.extractfile(member).read().decode(), "owner": "root"}
                elif member.isdir():
                    node[parts[-1]] = {"type": "dir", "owner": "root"}

    def log(self, command, status="success", message=""):
        """Logs a command execution."""
        # Removed the print statement for logging to the console

        # Add log entry to the log list
        self.log_actions.append({
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "status": status,
            "message": message
        })

    def save_log(self):
        """Saves the session log to an XML file."""
        # Check if there are any actions to log
        if not self.log_actions:
            print("No actions to log.")
            return

        root = ET.Element("session")
        for action in self.log_actions:
            entry = ET.SubElement(root, "action")
            for key, value in action.items():
                ET.SubElement(entry, key).text = value

        # Save log to XML file
        try:
            tree = ET.ElementTree(root)
            tree.write(self.log_path)
            print(f"Log saved to {self.log_path}")
        except Exception as e:
            print(f"Error saving log: {e}")

    def execute_command(self, command):
        """Executes a given shell command."""
        parts = command.strip().split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]

        if cmd == "ls":
            self.ls()
        elif cmd == "cd":
            self.cd(args)
        elif cmd == "chown":
            self.chown(args)
        elif cmd == "who":
            self.who()
        elif cmd == "uniq":
            self.uniq(args)
        elif cmd == "exit":
            self.exit_shell()
        else:
            print(f"Command not found: {cmd}")
            self.log(command, status="error", message="Command not found")

    def ls(self):
        """Lists files and directories in the current path."""
        node = self.traverse_path(self.current_path)
        if not isinstance(node, dict):
            print("Not a directory")
            self.log("ls", status="error", message="Not a directory")
            return
        for name in node:
            print(name)
        self.log("ls")

    def cd(self, args):
        """Changes the current working directory."""
        if len(args) != 1:
            print("Usage: cd <path>")
            self.log("cd", status="error", message="Invalid arguments")
            return
        path = args[0]
        new_path = os.path.normpath(os.path.join(self.current_path, path))
        if self.traverse_path(new_path) is None:
            print(f"No such directory: {path}")
            self.log("cd", status="error", message="No such directory")
        else:
            self.current_path = new_path
            self.log(f"cd {path}")

    def chown(self, args):
        """Changes the owner of a file or directory (mock implementation)."""
        if len(args) != 2:
            print("Usage: chown <owner> <path>")
            self.log("chown", status="error", message="Invalid arguments")
            return
        owner, path = args
        node = self.traverse_path(os.path.join(self.current_path, path))
        if node is None:
            print(f"No such file or directory: {path}")
            self.log("chown", status="error", message="No such file or directory")
        elif "owner" not in node:
            print(f"Cannot change owner of {path}")
            self.log("chown", status="error", message="Cannot change owner")
        else:
            node["owner"] = owner
            print(f"Owner of {path} changed to {owner}")
            self.log(f"chown {owner} {path}")

    def who(self):
        """Displays the current user."""
        print(f"User: {self.current_user}")
        self.log("who")

    def uniq(self, args):
        """Removes duplicate lines from a file."""
        if len(args) != 1:
            print("Usage: uniq <file>")
            self.log("uniq", status="error", message="Invalid arguments")
            return
        path = args[0]
        node = self.traverse_path(path)
        if node is None or node.get("type") != "file":
            print(f"No such file: {path}")
            self.log("uniq", status="error", message="No such file")
        else:
            lines = node["content"].splitlines()
            unique_lines = "\n".join(sorted(set(lines), key=lines.index))
            node["content"] = unique_lines
            print(unique_lines)
            self.log(f"uniq {path}")

    def exit_shell(self):
        """Exits the shell and saves the log."""
        self.save_log()
        print("Session saved. Exiting...")
        exit()

    def traverse_path(self, path):
        """Traverses the virtual file system to a given path."""
        parts = path.strip("\\").split("\\")
        node = self.fs
        for part in parts:
            if part == "":
                continue
            if part not in node or not isinstance(node[part], dict):
                return None
            node = node[part]
        return node

    def run(self):
        """Starts the shell emulator."""
        print("Welcome to Shell Emulator. Type 'exit' to quit.")
        while True:
            command = input(f"{self.current_path}> ")
            self.execute_command(command)


def main():
    parser = argparse.ArgumentParser(description="Shell Emulator for a UNIX-like OS.")
    parser.add_argument(
        "--tar", required=True, help="Path to the tar file representing the virtual file system."
    )
    parser.add_argument(
        "--log", required=True, help="Path to the XML log file."
    )

    args = parser.parse_args()

    try:
        # Initialize and run the shell emulator with provided arguments
        shell = ShellEmulator(tar_path=args.tar, log_path=args.log)
        shell.run()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
