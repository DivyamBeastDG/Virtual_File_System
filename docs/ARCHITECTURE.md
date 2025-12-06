# VFS Simulator – Architecture

## 1. Layered Design

### **User Space / GUI Layer**
- Implemented in the `VFSGuiApp` class (Tkinter GUI).
- Responsible for:
  - View rendering & layout
  - Handling button actions and double-click events
  - Displaying file tree (left panel)
  - Displaying statistics and live operation log (right panel)
  - Routing all user actions to the Virtual File System core

### **Virtual File System (VFS) Core Layer**
- Implemented in the `VirtualFileSystem` class.
- Acts as the OS-level Virtual File System layer.
- Provides system-call-like operations:
  - `create`, `delete`
  - `change_directory`
  - `read_file`, `write_file`
  - `get_current_items`
- Maintains:
  - In-memory simulated disk (`filesystem` dictionary)
  - Caching systems for faster lookup (dentry + inode)
  - Statistics and operation history

### **Filesystem Type / Abstraction Layer**
- Implemented using the `FileSystemType` enum.
- Supported filesystem types:
  - **EXT4, NTFS, FAT32, BTRFS, XFS, NFS**
- Changing the filesystem:
  - Reinitializes the VFS
  - Updates `/etc/config.txt` metadata
  - Appends logs to `/var/log/system.log`
  - Demonstrates how VFS mounts different underlying filesystems with a common interface

---

##
2. Core Data Structures

### **FSItem**
Represents both files and directories.

| Field | Description |
|--------|------------|
| `name` | Name of the file/directory |
| `item_type` | `FILE` or `DIRECTORY` |
| `inode` | Unique identifier |
| `created` | Timestamp of creation |
| `children` | Names of contained items (only for directories) |
| `content` | File content (only for files) |
| `size` | File size or number of children |

### **Filesystem Map**
```python
self.filesystem: Dict[str, FSItem]
```

Key format: full path (e.g. /home/user/readme.txt)

Value: FSItem object representing the inode

Functions as an in-memory disk

3. Caching System
Dentry Cache

self.dentry_cache: Dict[str, FSItem]

Used during directory navigation (change_directory)

Stores directory paths for faster access

Inode Cache

self.inode_cache: Dict[int, FSItem]

Used in read_file

Speeds up retrieval of frequently accessed files

Cache Statistics

cache_hits

cache_misses

Hit Rate (%) = hits / (hits + misses) * 100

All metrics displayed live on the GUI

4. Operation Log

Tracks history of all executed operations.

Field	Description
timestamp	Date & time of action
operation	e.g. CREATE, DELETE, READ, WRITE, CHDIR, READDIR
path	Target path
filesystem	Selected filesystem type
success	Bool status flag

Displayed in the right-panel scrolling log window.

5. Key Methods Overview
Initialization

_initialize_filesystem() creates basic structure:

/

/home/user/documents, /home/user/downloads

/home/user/readme.txt

/etc/config.txt

/var/log/system.log

Create & Delete

create(name, item_type) — creates a new file or directory

delete(name) — deletes a file or empty directory only

Navigation

change_directory(name) — supports normal names + ..

Uses dentry cache to improve performance

Read & Write

read_file(name) — reads content (uses inode cache)

write_file(name, content) — updates file data and size

6. GUI Structure
Region	Purpose
Top bar	Title + filesystem selection dropdown
Left panel	File explorer tree + action buttons
Right panel	Statistics + cache info + operations log
Popup windows	File view/edit + architecture explanation window

7. Design Goals

Demonstrate real OS VFS behavior visually

Keep implementation fully in-memory for conceptual clarity

Show performance impact of caching through real-time statistics

Provide live operation logs for viva and demonstration

Help understand the relationship between user space, VFS layer, and filesystem types
