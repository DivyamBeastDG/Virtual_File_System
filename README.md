# Virtual File System (VFS) Simulator

A desktop-based Virtual File System (VFS) simulator written in Python with a modern Tkinter GUI. This project is an educational tool to demonstrate fundamental OS file-system concepts such as hierarchical file structures, inodes, dentry & inode caching, system call logging, and performance metrics — all wrapped in an approachable user interface.

---

Table of contents
- [Demo](#demo)
- [Highlights](#highlights)
- [Features](#features)
- [Project structure & key classes](#project-structure--key-classes)
- [Installation](#installation)
- [Running the simulator](#running-the-simulator)
- [How to use the GUI](#how-to-use-the-gui)
- [VFS operations and behavior](#vfs-operations-and-behavior)
- [Implementation notes](#implementation-notes--extension-ideas)
- [Contributing](#contributing)

---

## Demo

Start the application and explore a small prepopulated VFS (root, /home/user, /etc, /var/log, etc.). You can create/delete files & directories, view and edit file contents, switch between simulated file system types (ext4, ntfs, fat32, btrfs, xfs, nfs), view caching stats and operation logs, and inspect an illustrated VFS architecture from the UI.

---

## Highlights

- Modern, dark-themed Tkinter GUI
- File/directory creation, deletion, reading, and writing
- Dentry (path) and Inode caching simulation with hit/miss counting
- Real-time operation logging (CREATE, READ, WRITE, CHDIR, READDIR, DELETE, CACHE_CLEAR)
- Multi-filesystem mounting simulation (ext4, NTFS, FAT32, BTRFS, XFS, NFS)
- Small, self-contained Python codebase (no external dependencies beyond the standard library)

---

## Features

- GUI file browser with:
  - Double-click navigation
  - Create file/folder, Delete, View, Edit, Refresh
  - Parent directory navigation (`..`), Home and Back buttons
- Statistics dashboard:
  - Total files, total directories
  - Total operations
  - Cache hits, cache misses and hit rate
- Operation log viewer (most recent 50 operations)
- Clear Dentry & Inode caches to simulate cache misses
- Mounting a different filesystem resets the VFS to a clean prepopulated state
- VFS architecture viewer describing layers and concepts

---

## Project structure & key classes

- `vfs.py` — the main file that contains the entire simulator (GUI + backend).
  - `FileSystemType` (Enum): Supported filesystem identifiers (ext4, ntfs, fat32, btrfs, xfs, nfs).
  - `ItemType` (Enum): FILE or DIRECTORY.
  - `FSItem` (dataclass): Representation of a file/directory, including name, inode, creation time, size, content and children.
  - `Operation` (dataclass): Small struct used for operation logging (timestamp, operation name, path, filesystem, success).
  - `Statistics`: Tracks counts for files, directories, operations, cache hits and misses.
  - `VirtualFileSystem`: Core logic that maintains an in-memory map of path → FSItem, simulates inodes, dentry & inode caches, and logs operations.
  - `VFSGuiApp`: Tkinter GUI that binds user actions to `VirtualFileSystem` methods, renders file lists, stats, and operation logs.

---

## Installation

Requirements:
- Python 3.7+ (stdlib only; Tkinter is required and typically bundled with standard Python distributions)

Clone the repo (or download the `vfs.py` file) and run:

```bash
git clone https://github.com/DivyamBeastDG/Virtual_File_System.git
cd Virtual_File_System
```

No extra pip packages are required.

---

## Running the simulator

From the project root:

```bash
python vfs.py
```

This will launch the GUI window and initialize the simulated VFS with a small default structure:
- `/` (root)
- `/home/user/` with sample files (e.g. `readme.txt`)
- `/etc/config.txt`
- `/var/log/system.log`

---

## How to use the GUI

Left panel — File Explorer
- Double-click a folder to navigate into it.
- Use the Home (🏠) button to jump back to `/`.
- Use Back (⬅️) to go up one directory (`..`).
- Toolbar:
  - "📁 New Folder" — create a directory in the current folder
  - "📄 New File" — create an empty file in the current folder
  - "🗑️ Delete" — delete selected file or empty directory (won't permit deleting non-empty directories)
  - "👁️ View" — open a read-only window to view file contents
  - "✏️ Edit" — open an editor window, modify and save contents back to the VFS
  - "🔄 Refresh" — refresh the file list and stats

Right panel — Stats & Log
- Live counts for files, directories, and operations
- Cache Hits / Cache Misses and a computed Hit Rate
- Operation log viewer lists recent system calls and their status (success/failure)
- "🗑️ Clear Cache" clears dentry and inode caches to demonstrate cache miss behavior
- "File System" combobox (top-right) allows switching the simulated file system (resets the VFS)

"🏗️ View VFS Architecture" shows a descriptive document that explains the VFS layering and common system call flow.

---

## VFS operations and behavior (implementation detail)

- Path mapping: The simulator keeps an in-memory dictionary mapping full paths (strings) to `FSItem`.
- Inode simulation: Each created item receives an incrementing numeric inode ID.
- Caches:
  - Dentry cache maps paths → FSItem (simulates directory-entry path resolution caching).
  - Inode cache maps inode IDs → FSItem (simulates caching file metadata/content).
  - Cache hits/misses are counted when `change_directory()` or `read_file()` are called and an entry exists/does not exist in the relevant cache.
- Operation logging: Every user action that interacts with the VFS is logged as an `Operation` with a timestamp and success state. The log displays the last 50 operations.
- Safety checks:
  - Prevent creating items with invalid names (empty or containing `/`).
  - Prevent creating items that already exist.
  - Prevent deleting non-empty directories.

---

## Example flows

- Create a folder:
  1. Click "📁 New Folder"
  2. Enter a valid name (no slashes)
  3. The GUI will show a success message and refresh the listing

- View & edit a file:
  1. Select a file and click "👁️ View" to read contents
  2. Select a file and click "✏️ Edit" to modify; click "💾 Save" to write back
  3. Saving triggers a `WRITE` operation; reading triggers a `READ` operation and may update the inode cache

- Simulate cache behavior:
  1. Perform directory changes and reads to populate caches
  2. Inspect "Cache Hits" and "Cache Misses" counters in the right panel
  3. Click "🗑️ Clear Cache" to flush caches; subsequent operations will produce misses until caches are repopulated

---

## Implementation notes & extension ideas

- `vfs.py` is self-contained and small — a good starting point for demonstrations and classroom use.
- Possible extensions:
  - Persist the virtual filesystem to disk (e.g. JSON file) so changes survive restarts
  - Add permission/ownership simulation and access checks (r/w/x)
  - Add simulated block-level read/write latency or I/O statistics
  - Add a searchable operation log and filtering (by operation type, path, success/failure)
  - Add visual diagrams and richer architecture views
  - Add automated tests for the `VirtualFileSystem` API

---

## Contributing

Contributions, suggestions and fixes are welcome. Please open issues for feature requests or bug reports, and submit pull requests for proposed code changes. Keep changes small and focused for easier review.

---

Acknowledgements
- Built for educational purposes to illustrate core VFS concepts with a GUI frontend and a compact Python backend.
