# VFS Simulator – Architecture

## 1. Layered Design

### **User Space / GUI Layer**
- Implemented in the `VFSGuiApp` class (Tkinter GUI).
- Responsible for:
  - View and event handling (buttons, inputs, double-click navigation)
  - Displaying file tree (left side) and statistics/log window (right side)
  - Routing user actions to the VFS core

### **Virtual File System (VFS) Core Layer**
- Implemented in the `VirtualFileSystem` class.
- Acts like the Virtual File System layer in an operating system.
- Provides system-call-like methods:
  - `create`, `delete`
  - `change_directory`
  - `read_file`, `write_file`
  - `get_current_items`
- Maintains:
  - In-memory simulated disk via a dictionary (`filesystem`)
  - Caching systems (dentry + inode)
  - Operation log & statistics

### **Filesystem Type / Abstraction Layer**
- Implemented using the `FileSystemType` enum.
- Supported types: **EXT4, NTFS, FAT32, BTRFS, XFS, NFS**
- Changing filesystem:
  - Re-initializes VFS
  - Updates `/etc/config.txt` and `/var/log/system.log`
  - Demonstrates concept of mounting different file systems under VFS

---

## 2. Core Data Structures

### **FSItem**
Represents both files and directories.

| Field | Description |
|--------|-------------|
| `name` | Item name |
| `item_type` | `FILE` or `DIRECTORY` (`ItemType` enum) |
| `inode` | Unique identifier |
| `created` | Timestamp |
| `children` | Items inside directory (only for directories) |
| `content` | File contents (only for files) |
| `size` | File size or child count |

### **Filesystem Map**
```python
self.filesystem: Dict[str, FSItem]


Caching
Dentry Cache

self.dentry_cache: Dict[str, FSItem]

Used in change_directory()

Stores directory paths to speed up navigation

Inode Cache

self.inode_cache: Dict[int, FSItem]

Used in read_file()

Stores inode-to-file mapping

Tracking:

cache_hits

cache_misses

Calculated hit rate (%)

Operation Log
Field	Description
timestamp	Date & time
operation	CREATE / DELETE / READ / WRITE / CHDIR / READDIR
path	File/directory path
filesystem	Selected filesystem type
success	Operation result
3. Key Methods Overview
Initialization

_initialize_filesystem() creates:

/

/home/user/documents, /home/user/downloads

/home/user/readme.txt

/etc/config.txt

/var/log/system.log

Create & Delete

create(name, item_type) — create file/directory

delete(name) — delete file or empty directory

Navigation

change_directory(name) — supports names + ..

Uses dentry cache for faster lookups

Read & Write

read_file(name) — uses inode cache

write_file(name, content) — modifies file data

4. GUI Structure
Region	Purpose
Top bar	Title + filesystem dropdown
Left panel	Tree-view file explorer + action buttons
Right panel	Statistics + cache info + log
Popup windows	File view/edit + architecture explanation
5. Design Goals

Demonstrate real OS VFS behaviour visually

Keep implementation fully in-memory for clarity

Show impact of caching through real-time metrics

Make VFS internal behaviour observable for viva/presentation
