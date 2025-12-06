**Purpose:** This is your “mini report” that directly links project ↔ OS theory.  

Create `docs/OS_REPORT.md` and paste:

```markdown
# Virtual File System (VFS) Simulator – OS Concepts Report

## 1. Aim

To design and implement a **Virtual File System (VFS) Simulator** that explains:

- How the VFS layer hides differences between filesystem types.
- How files and directories are represented using **inodes**.
- How **dentry cache** and **inode cache** improve performance.
- How basic file-related system calls behave internally.

---

## 2. Virtual File System Layer

In an operating system:

- User processes do not talk directly to EXT4, NTFS, etc.
- They use a common interface (`open`, `read`, `write`, `close`).
- The **VFS layer** translates these calls to the correct filesystem implementation.

In this project:

- The class `VirtualFileSystem` plays the role of the VFS.
- The Tkinter GUI (`VFSGuiApp`) behaves like user programs.
- Main operations:
  - `create`, `delete`
  - `change_directory`
  - `read_file`, `write_file`
  - `get_current_items`

Each call is logged as an `Operation` with timestamp, operation name, path, filesystem and success flag.

---

## 3. Inodes and Directory Structure

- Every file/directory is represented by an `FSItem` object.
- Each `FSItem` has a unique `inode` number.
- A dictionary `filesystem: Dict[str, FSItem]` maps **absolute path** to `FSItem`.
- Directories maintain a `children` list with names of contained files/subdirectories.

This models:

- **Inode-based identification** of files.
- **Hierarchical directory tree** using paths like `/home/user/documents`.

---

## 4. Caching: Dentry and Inode

### 4.1 Dentry Cache

- Dentry = directory entry (maps name → inode).
- Real OSs cache dentries to speed up path lookup.

In this project:

- Implemented using `dentry_cache: Dict[str, FSItem]`.
- Key: directory path.
- Used inside `change_directory()`:
  - First visit → cache miss, directory added to cache.
  - Next visits → cache hit.

### 4.2 Inode Cache

- Inode cache stores metadata of recently used files.

In this project:

- Implemented using `inode_cache: Dict[int, FSItem]`.
- Used in `read_file()`:
  - If inode exists in cache → hit.
  - Else → miss and insert into cache.

A **“Clear Cache”** button resets both caches to illustrate the effect of caching.

---

## 5. Simulated System Calls

The following table shows how our operations correspond to typical file system calls:

| Operation | Meaning in project                             | Real OS equivalent              |
|----------|-------------------------------------------------|---------------------------------|
| CREATE   | Make file or directory in current path          | `creat`, `mkdir`                |
| DELETE   | Remove file or empty directory                  | `unlink`, `rmdir`               |
| READ     | Open and read file content                      | `open + read`                   |
| WRITE    | Modify existing file content                    | `write`                         |
| CHDIR    | Change current directory                        | `chdir`                         |
| READDIR  | List contents of current directory              | `readdir`                       |

Each operation updates statistics and is written into the log visible in the GUI.

---

## 6. Multiple Filesystems

Supported types in the simulator:

- EXT4, NTFS, FAT32, BTRFS, XFS, NFS

Behaviour:

- User selects filesystem type from a dropdown.
- A new in-memory filesystem is initialised.
- Configuration is written to `/etc/config.txt`.
- Log entries are appended to `/var/log/system.log`.

This shows that:

- From the application point of view, the VFS API stays the same.
- Only the underlying filesystem changes.

---

## 7. Performance Metrics

The simulator tracks:

- Total files
- Total directories
- Total operations performed
- Cache hits and misses
- Cache hit rate (%)

These metrics are updated in real time and displayed on the right panel of the GUI.  
They help demonstrate how repeated operations become faster due to caching.

---

## 8. Limitations and Future Scope

**Limitations:**

- No permanent disk storage (state is lost when program exits).
- No user/group permissions or ownership.
- No block-level allocation, fragmentation or journaling.

**Future Enhancements:**

- Save/load the filesystem to/from a JSON file.
- Add permission bits (r/w/x) and enforce access checks.
- Simulate different allocation strategies for files.
- Add a simple journaling mechanism to simulate crash recovery.

---

## 9. Conclusion

The **Virtual File System Simulator** successfully demonstrates:

- The role of the **VFS layer** between user programs and concrete filesystems.
- Representation of files and directories using **inodes** and paths.
- Importance of **dentry** and **inode** caches for performance.
- Basic system call behaviour for file operations.
- Concept of supporting multiple filesystem types under one unified interface.

This makes the project suitable as a practical component for an Operating Systems course.
