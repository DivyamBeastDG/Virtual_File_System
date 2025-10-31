# Virtual_File_System
Virtual File System (VFS) Simulator
Overview
The Virtual File System (VFS) Simulator is a Python-based desktop application built using Tkinter. It serves as an educational tool to demonstrate fundamental concepts of a modern operating system's file system layer.

It abstracts the underlying storage mechanisms to allow users to interact with files and directories, while providing real-time logging and performance statistics for operations like file creation, reading, and directory traversal, specifically highlighting the role of Dentry and Inode Caching.

Key Features
GUI Interface: A modern, dark-themed user interface (GUI) built with Tkinter for intuitive file system interaction.

Virtual File System Model: Simulates a hierarchical file structure with support for files, directories, and unique Inodes.

System Call Logging: Records and displays a log of every file system operation (e.g., CREATE, READDIR, CHDIR, READ, WRITE).

Caching Simulation: Includes logic for Dentry Cache (directory entries) and Inode Cache, and tracks Cache Hits and Cache Misses in real-time.

Statistics Panel: Displays key performance metrics, including total files/directories, total operations, and cache hit rate.

Multi-Filesystem Support: Allows for "mounting" and simulating different file system types (e.g., EXT4, NTFS, BTRFS) for demonstration purposes.

Installation and Usage
Prerequisites

You need Python 3.x installed on your system. The program only relies on standard built-in Python libraries.

Running the Simulator

Save the Code: Save the provided Python code into a file named, for example, vfs_simulator.py.

Execute the Script: Open your terminal or command prompt, navigate to the directory where you saved the file, and run:

Bash
python vfs_simulator.py
The GUI window will open, and the VFS will be initialized with a base structure (root, home/user, etc.).

How to Use
The application is split into two main panels:

Left Panel: File Explorer

Navigation: Double-click on a folder to navigate into it, or double-click the .. entry to go up to the parent directory. You can also use the (Home) and (Back) buttons.

Operations: Use the toolbar buttons for:

New Folder/File: Prompts for a name to create an item in the current directory.

Delete: Removes the selected file or an empty directory.

View/Edit: Opens a separate window to view or modify the content of a selected file.

Columns: Displays crucial VFS information: Name, Type (FILE/DIR), Size/Items, Inode (a unique ID), and Creation Timestamp.

Right Panel: Statistics and Log

System Statistics: Watch these counters to understand the VFS's performance:

Cache Hits/Misses: Increases when file or directory lookup uses (Hit) or misses (Miss) the in-memory cache.

Hit Rate: Indicates the efficiency of the caching mechanism.

Operations Log: Displays the 50 most recent system calls, noting the operation (READ, WRITE, CHDIR, etc.), the path, and a success status.

Clear Cache: Clear Cache button to manually flush the Dentry and Inode caches, demonstrating how subsequent operations will incur Cache Misses until the caches are repopulated.

Change File System: Use the dropdown menu in the top right to re-mount the VFS with a different, purely illustrative file system type.

Project Structure
The Python file is organized around key classes:

Class	Description
FileSystemType (Enum)	Defines supported file system types (e.g., EXT4, NTFS).
ItemType (Enum)	Defines content types: FILE or DIRECTORY.
FSItem (dataclass)	Represents a single file or directory, including inode, name, content, and list of children.
Operation (dataclass)	Data structure for logging system activities.
Statistics	Tracks file/directory counts and cache performance.
VirtualFileSystem	The core logic. Handles operations (create, delete, chdir), maintains the file system structure (self.filesystem), and manages the caches and log.
VFSGuiApp	The Tkinter application class. Handles the GUI creation, styling, button logic, and connecting user actions to the VirtualFileSystem backend.
