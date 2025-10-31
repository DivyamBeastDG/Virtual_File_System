import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

class FileSystemType(Enum):
    EXT4 = "ext4"
    NTFS = "ntfs"
    FAT32 = "fat32"
    BTRFS = "btrfs"
    XFS = "xfs"
    NFS = "nfs"

class ItemType(Enum):
    FILE = "file"
    DIRECTORY = "dir"

@dataclass
class FSItem:
    name: str
    item_type: ItemType
    inode: int
    created: str
    children: List[str] = field(default_factory=list)
    content: str = ""
    size: int = 0

@dataclass
class Operation:
    timestamp: str
    operation: str
    path: str
    filesystem: str
    success: bool = True

class Statistics:
    def __init__(self):
        self.total_files = 0
        self.total_dirs = 0
        self.operations = 0
        self.cache_hits = 0
        self.cache_misses = 0

class VirtualFileSystem:
    def __init__(self, fs_type: FileSystemType = FileSystemType.EXT4):
        self.fs_type = fs_type
        self.filesystem: Dict[str, FSItem] = {}
        self.current_path = "/"
        self.inode_counter = 0
        self.stats = Statistics()
        self.operation_log: List[Operation] = []
        self.dentry_cache: Dict[str, FSItem] = {}
        self.inode_cache: Dict[int, FSItem] = {}
        self._initialize_filesystem()
    
    def _initialize_filesystem(self):
        self._create_item_internal("/", "root", ItemType.DIRECTORY)
        self._create_item_internal("/", "home", ItemType.DIRECTORY)
        self._create_item_internal("/home", "user", ItemType.DIRECTORY)
        self._create_item_internal("/home/user", "documents", ItemType.DIRECTORY)
        self._create_item_internal("/home/user", "downloads", ItemType.DIRECTORY)
        
        readme = self._create_item_internal("/home/user", "readme.txt", ItemType.FILE)
        readme.content = "Welcome to VFS Simulator\nThis demonstrates Virtual File System operations with modern GUI.\n\nFeatures:\n- Multi-file system support\n- Dentry and Inode caching\n- System call logging\n- Performance statistics"
        readme.size = len(readme.content)
        
        self._create_item_internal("/", "etc", ItemType.DIRECTORY)
        config = self._create_item_internal("/etc", "config.txt", ItemType.FILE)
        config.content = f"filesystem={self.fs_type.value}\ncache_enabled=true\nversion=2.0\narchitecture=x64"
        config.size = len(config.content)
        
        self._create_item_internal("/", "var", ItemType.DIRECTORY)
        self._create_item_internal("/var", "log", ItemType.DIRECTORY)
        
        log = self._create_item_internal("/var/log", "system.log", ItemType.FILE)
        log.content = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] System initialized\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] File system mounted: {self.fs_type.value}"
        log.size = len(log.content)
        
        self._update_stats()
    
    def _create_item_internal(self, parent_path: str, name: str, item_type: ItemType) -> FSItem:
        self.inode_counter += 1
        
        item = FSItem(
            name=name,
            item_type=item_type,
            inode=self.inode_counter,
            created=datetime.now().isoformat()
        )
        
        if parent_path == "/":
            full_path = f"/{name}" if name != "root" else "/"
        else:
            full_path = f"{parent_path}/{name}"
        
        self.filesystem[full_path] = item
        
        if parent_path in self.filesystem and name != "root":
            self.filesystem[parent_path].children.append(name)
        
        return item
    
    def _update_stats(self):
        self.stats.total_files = sum(1 for item in self.filesystem.values() 
                                      if item.item_type == ItemType.FILE)
        self.stats.total_dirs = sum(1 for item in self.filesystem.values() 
                                     if item.item_type == ItemType.DIRECTORY)
    
    def _log_operation(self, operation: str, path: str, success: bool = True):
        op = Operation(
            timestamp=datetime.now().strftime("%H:%M:%S.%f")[:-3],
            operation=operation,
            path=path,
            filesystem=self.fs_type.value,
            success=success
        )
        self.operation_log.append(op)
        self.stats.operations += 1
    
    def create(self, name: str, item_type: ItemType) -> tuple[bool, str]:
        if not name or '/' in name:
            return False, "Invalid name!"
        
        new_path = f"{self.current_path}/{name}" if self.current_path != "/" else f"/{name}"
        
        if new_path in self.filesystem:
            self._log_operation("CREATE", new_path, False)
            return False, "Item already exists!"
        
        self.inode_counter += 1
        item = FSItem(
            name=name,
            item_type=item_type,
            inode=self.inode_counter,
            created=datetime.now().isoformat()
        )
        
        self.filesystem[new_path] = item
        self.filesystem[self.current_path].children.append(name)
        
        self._update_stats()
        self._log_operation("CREATE", new_path)
        return True, f"Created {item_type.value}: {name}"
    
    def delete(self, name: str) -> tuple[bool, str]:
        item_path = f"{self.current_path}/{name}" if self.current_path != "/" else f"/{name}"
        
        if item_path not in self.filesystem:
            self._log_operation("DELETE", item_path, False)
            return False, "Item not found!"
        
        item = self.filesystem[item_path]
        
        if item.item_type == ItemType.DIRECTORY and item.children:
            self._log_operation("DELETE", item_path, False)
            return False, "Cannot delete non-empty directory!"
        
        del self.filesystem[item_path]
        self.filesystem[self.current_path].children.remove(name)
        
        if item_path in self.dentry_cache:
            del self.dentry_cache[item_path]
        if item.inode in self.inode_cache:
            del self.inode_cache[item.inode]
        
        self._update_stats()
        self._log_operation("DELETE", item_path)
        return True, f"Deleted: {name}"
    
    def change_directory(self, name: str) -> tuple[bool, str]:
        if name == "..":
            if self.current_path != "/":
                parts = self.current_path.split('/')
                self.current_path = '/'.join(parts[:-1]) or '/'
                self._log_operation("CHDIR", self.current_path)
                return True, f"Changed to {self.current_path}"
            return False, "Already at root"
        
        new_path = f"{self.current_path}/{name}" if self.current_path != "/" else f"/{name}"
        
        if new_path not in self.filesystem:
            return False, "Directory not found!"
        
        item = self.filesystem[new_path]
        
        if item.item_type != ItemType.DIRECTORY:
            return False, "Not a directory!"
        
        if new_path in self.dentry_cache:
            self.stats.cache_hits += 1
        else:
            self.dentry_cache[new_path] = item
            self.stats.cache_misses += 1
        
        self.current_path = new_path
        self._log_operation("CHDIR", new_path)
        return True, f"Changed to {new_path}"
    
    def read_file(self, name: str) -> Optional[FSItem]:
        file_path = f"{self.current_path}/{name}" if self.current_path != "/" else f"/{name}"
        
        if file_path not in self.filesystem:
            return None
        
        item = self.filesystem[file_path]
        
        if item.item_type != ItemType.FILE:
            return None
        
        if item.inode in self.inode_cache:
            self.stats.cache_hits += 1
        else:
            self.inode_cache[item.inode] = item
            self.stats.cache_misses += 1
        
        self._log_operation("READ", file_path)
        return item
    
    def write_file(self, name: str, content: str) -> tuple[bool, str]:
        file_path = f"{self.current_path}/{name}" if self.current_path != "/" else f"/{name}"
        
        if file_path not in self.filesystem:
            self._log_operation("WRITE", file_path, False)
            return False, "File not found!"
        
        item = self.filesystem[file_path]
        
        if item.item_type != ItemType.FILE:
            self._log_operation("WRITE", file_path, False)
            return False, "Not a file!"
        
        item.content = content
        item.size = len(content)
        
        self._log_operation("WRITE", file_path)
        return True, f"File saved: {name}"
    
    def get_current_items(self) -> List[FSItem]:
        current = self.filesystem.get(self.current_path)
        if not current or current.item_type != ItemType.DIRECTORY:
            return []
        
        items = []
        for child_name in sorted(current.children):
            child_path = f"{self.current_path}/{child_name}" if self.current_path != "/" else f"/{child_name}"
            child = self.filesystem.get(child_path)
            if child:
                items.append(child)
        
        self._log_operation("READDIR", self.current_path)
        return items
    
    def clear_cache(self):
        self.dentry_cache.clear()
        self.inode_cache.clear()
        self._log_operation("CACHE_CLEAR", "system")

class VFSGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual File System Simulator - OS Evaluation Project")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        self.colors = {
            'bg': '#1e1e1e',
            'sidebar': '#252526',
            'panel': '#2d2d30',
            'accent': '#007acc',
            'success': '#4ec9b0',
            'error': '#f48771',
            'text': '#cccccc',
            'text_dim': '#858585',
            'border': '#3e3e42'
        }
        
        self.vfs = VirtualFileSystem(FileSystemType.EXT4)
        
        self.setup_styles()
        self.create_widgets()
        self.refresh_file_list()
        self.update_stats()
        self.root.after(100, self.scroll_to_bottom_log)
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Custom.Treeview",
                       background=self.colors['panel'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['panel'],
                       borderwidth=0,
                       font=('Segoe UI', 10))
        style.map('Custom.Treeview',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])
        
        style.configure("Custom.Treeview.Heading",
                       background=self.colors['sidebar'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='flat',
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure("Accent.TButton",
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 9))
        
    def create_widgets(self):
        top_bar = tk.Frame(self.root, bg=self.colors['sidebar'], height=60)
        top_bar.pack(fill='x', side='top')
        top_bar.pack_propagate(False)
        
        title_label = tk.Label(top_bar, 
                               text="🖥️  Virtual File System Simulator",
                               bg=self.colors['sidebar'],
                               fg=self.colors['success'],
                               font=('Segoe UI', 18, 'bold'))
        title_label.pack(side='left', padx=20, pady=15)
        
        fs_frame = tk.Frame(top_bar, bg=self.colors['sidebar'])
        fs_frame.pack(side='right', padx=20)
        
        tk.Label(fs_frame, text="File System:", 
                bg=self.colors['sidebar'], 
                fg=self.colors['text'],
                font=('Segoe UI', 10)).pack(side='left', padx=5)
        
        self.fs_var = tk.StringVar(value=self.vfs.fs_type.value)
        fs_combo = ttk.Combobox(fs_frame, textvariable=self.fs_var,
                               values=[fs.value for fs in FileSystemType],
                               state='readonly', width=10,
                               font=('Segoe UI', 10))
        fs_combo.pack(side='left', padx=5)
        fs_combo.bind('<<ComboboxSelected>>', self.change_filesystem)
        
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        left_panel = tk.Frame(main_container, bg=self.colors['panel'], width=600)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        path_frame = tk.Frame(left_panel, bg=self.colors['sidebar'], height=45)
        path_frame.pack(fill='x', pady=(0, 5))
        path_frame.pack_propagate(False)
        
        btn_frame = tk.Frame(path_frame, bg=self.colors['sidebar'])
        btn_frame.pack(side='left', padx=10)
        
        home_btn = tk.Button(btn_frame, text="🏠", bg=self.colors['panel'],
                            fg=self.colors['text'], relief='flat',
                            font=('Segoe UI', 12), width=3,
                            command=self.go_home, cursor='hand2')
        home_btn.pack(side='left', padx=2)
        
        back_btn = tk.Button(btn_frame, text="⬅️", bg=self.colors['panel'],
                            fg=self.colors['text'], relief='flat',
                            font=('Segoe UI', 12), width=3,
                            command=self.go_back, cursor='hand2')
        back_btn.pack(side='left', padx=2)
        
        self.path_label = tk.Label(path_frame, text=self.vfs.current_path,
                                   bg=self.colors['sidebar'],
                                   fg=self.colors['success'],
                                   font=('Consolas', 11, 'bold'),
                                   anchor='w')
        self.path_label.pack(side='left', fill='x', expand=True, padx=10)
        
        toolbar = tk.Frame(left_panel, bg=self.colors['sidebar'], height=50)
        toolbar.pack(fill='x', pady=(0, 5))
        toolbar.pack_propagate(False)
        
        buttons = [
            ("📁 New Folder", self.create_directory),
            ("📄 New File", self.create_file),
            ("🗑️ Delete", self.delete_item),
            ("👁️ View", self.view_file),
            ("✏️ Edit", self.edit_file),
            ("🔄 Refresh", self.refresh_file_list)
        ]
        
        for text, command in buttons:
            btn = tk.Button(toolbar, text=text, command=command,
                          bg=self.colors['accent'], fg='white',
                          relief='flat', font=('Segoe UI', 9),
                          padx=12, pady=8, cursor='hand2')
            btn.pack(side='left', padx=5, pady=8)
        
        file_frame = tk.Frame(left_panel, bg=self.colors['panel'])
        file_frame.pack(fill='both', expand=True)
        
        columns = ('Type', 'Size/Items', 'Inode', 'Created')
        self.tree = ttk.Treeview(file_frame, columns=columns, 
                                show='tree headings', style='Custom.Treeview')
        
        self.tree.heading('#0', text='Name', anchor='w')
        self.tree.heading('Type', text='Type', anchor='w')
        self.tree.heading('Size/Items', text='Size/Items', anchor='w')
        self.tree.heading('Inode', text='Inode', anchor='w')
        self.tree.heading('Created', text='Created', anchor='w')
        
        self.tree.column('#0', width=250, minwidth=150)
        self.tree.column('Type', width=80, minwidth=60)
        self.tree.column('Size/Items', width=120, minwidth=80)
        self.tree.column('Inode', width=80, minwidth=60)
        self.tree.column('Created', width=150, minwidth=100)
        
        scrollbar = ttk.Scrollbar(file_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        right_panel = tk.Frame(main_container, bg=self.colors['panel'], width=400)
        right_panel.pack(side='right', fill='both', padx=(5, 0))
        right_panel.pack_propagate(False)
        
        stats_label = tk.Label(right_panel, text="📊 System Statistics",
                              bg=self.colors['sidebar'], fg=self.colors['text'],
                              font=('Segoe UI', 12, 'bold'), anchor='w',
                              padx=15, pady=10)
        stats_label.pack(fill='x')
        
        stats_frame = tk.Frame(right_panel, bg=self.colors['panel'])
        stats_frame.pack(fill='x', padx=15, pady=10)
        
        self.stats_labels = {}
        stats_items = [
            ('files', '📄 Total Files:', '0'),
            ('dirs', '📁 Total Directories:', '0'),
            ('ops', '⚡ Operations:', '0'),
            ('hits', '✅ Cache Hits:', '0'),
            ('misses', '❌ Cache Misses:', '0'),
            ('rate', '📈 Hit Rate:', '0%')
        ]
        
        for key, label, value in stats_items:
            row = tk.Frame(stats_frame, bg=self.colors['panel'])
            row.pack(fill='x', pady=5)
            
            tk.Label(row, text=label, bg=self.colors['panel'],
                    fg=self.colors['text_dim'], font=('Segoe UI', 9),
                    anchor='w', width=20).pack(side='left')
            
            val_label = tk.Label(row, text=value, bg=self.colors['panel'],
                                fg=self.colors['success'], font=('Consolas', 10, 'bold'),
                                anchor='w')
            val_label.pack(side='left')
            self.stats_labels[key] = val_label
        
        cache_btn = tk.Button(stats_frame, text="🗑️ Clear Cache",
                             command=self.clear_cache,
                             bg=self.colors['error'], fg='white',
                             relief='flat', font=('Segoe UI', 9),
                             padx=15, pady=8, cursor='hand2')
        cache_btn.pack(pady=15)
        
        log_label = tk.Label(right_panel, text="📝 Operations Log",
                            bg=self.colors['sidebar'], fg=self.colors['text'],
                            font=('Segoe UI', 12, 'bold'), anchor='w',
                            padx=15, pady=10)
        log_label.pack(fill='x', pady=(20, 0))
        
        log_frame = tk.Frame(right_panel, bg=self.colors['panel'])
        log_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame,
                                                  bg=self.colors['bg'],
                                                  fg=self.colors['text'],
                                                  font=('Consolas', 8),
                                                  wrap='word',
                                                  relief='flat',
                                                  borderwidth=0)
        self.log_text.pack(fill='both', expand=True)
        
        arch_btn = tk.Button(right_panel, text="🏗️ View VFS Architecture",
                            command=self.show_architecture,
                            bg=self.colors['accent'], fg='white',
                            relief='flat', font=('Segoe UI', 9),
                            padx=15, pady=10, cursor='hand2')
        arch_btn.pack(fill='x', padx=15, pady=(10, 15))
    
    def refresh_file_list(self):
        self.tree.delete(*self.tree.get_children())
        
        if self.vfs.current_path != "/":
            self.tree.insert('', 'end', text='..', values=('DIR', '<parent>', '', ''),
                           tags=('parent',))
        
        items = self.vfs.get_current_items()
        
        for item in items:
            if item.item_type == ItemType.DIRECTORY:
                icon = '📁'
                size_info = f'{len(item.children)} items'
            else:
                icon = '📄'
                size_info = f'{item.size} bytes'
            
            created = datetime.fromisoformat(item.created).strftime('%Y-%m-%d %H:%M')
            
            self.tree.insert('', 'end', text=f'{icon} {item.name}',
                           values=(item.item_type.value.upper(), size_info, 
                                  item.inode, created),
                           tags=(item.item_type.value,))
        
        self.path_label.config(text=self.vfs.current_path)
        self.update_stats()
        self.update_log()
    
    def update_stats(self):
        stats = self.vfs.stats
        self.stats_labels['files'].config(text=str(stats.total_files))
        self.stats_labels['dirs'].config(text=str(stats.total_dirs))
        self.stats_labels['ops'].config(text=str(stats.operations))
        self.stats_labels['hits'].config(text=str(stats.cache_hits))
        self.stats_labels['misses'].config(text=str(stats.cache_misses))
        
        total_cache = stats.cache_hits + stats.cache_misses
        hit_rate = (stats.cache_hits / total_cache * 100) if total_cache > 0 else 0
        self.stats_labels['rate'].config(text=f'{hit_rate:.1f}%')
    
    def update_log(self):
        self.log_text.delete('1.0', 'end')
        
        for op in reversed(self.vfs.operation_log[-50:]):
            status = '✓' if op.success else '✗'
            color = self.colors['success'] if op.success else self.colors['error']
            
            log_line = f"[{op.timestamp}] {status} {op.operation:12} {op.path}\n"
            self.log_text.insert('1.0', log_line)
        
        self.log_text.see('1.0')
    
    def scroll_to_bottom_log(self):
        self.log_text.see('end')
    
    def on_item_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        name = item['text']
        
        if name.startswith('📁'):
            name = name[2:].strip()
            self.vfs.change_directory(name)
            self.refresh_file_list()
        elif name == '..':
            self.go_back()
        elif name.startswith('📄'):
            name = name[2:].strip()
            self.view_file()
    
    def go_home(self):
        self.vfs.current_path = '/'
        self.vfs._log_operation("CHDIR", '/')
        self.refresh_file_list()
    
    def go_back(self):
        self.vfs.change_directory('..')
        self.refresh_file_list()
    
    def create_directory(self):
        name = simpledialog.askstring("New Directory", "Enter directory name:",
                                     parent=self.root)
        if name:
            success, msg = self.vfs.create(name, ItemType.DIRECTORY)
            if success:
                messagebox.showinfo("Success", msg, parent=self.root)
                self.refresh_file_list()
            else:
                messagebox.showerror("Error", msg, parent=self.root)
    
    def create_file(self):
        name = simpledialog.askstring("New File", "Enter file name:",
                                     parent=self.root)
        if name:
            success, msg = self.vfs.create(name, ItemType.FILE)
            if success:
                messagebox.showinfo("Success", msg, parent=self.root)
                self.refresh_file_list()
            else:
                messagebox.showerror("Error", msg, parent=self.root)
    
    def delete_item(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete",
                                 parent=self.root)
            return
        
        item = self.tree.item(selection[0])
        name = item['text']
        
        if name.startswith('📁') or name.startswith('📄'):
            name = name[2:].strip()
        elif name == '..':
            return
        
        if messagebox.askyesno("Confirm Delete", 
                               f"Are you sure you want to delete '{name}'?",
                               parent=self.root):
            success, msg = self.vfs.delete(name)
            if success:
                messagebox.showinfo("Success", msg, parent=self.root)
                self.refresh_file_list()
            else:
                messagebox.showerror("Error", msg, parent=self.root)
    
    def view_file(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to view",
                                 parent=self.root)
            return
        
        item = self.tree.item(selection[0])
        name = item['text']
        
        if not name.startswith('📄'):
            messagebox.showwarning("Warning", "Please select a file",
                                 parent=self.root)
            return
        
        name = name[2:].strip()
        file_item = self.vfs.read_file(name)
        
        if file_item:
            viewer = tk.Toplevel(self.root)
            viewer.title(f"View: {name}")
            viewer.geometry("700x500")
            viewer.configure(bg=self.colors['bg'])
            
            header = tk.Frame(viewer, bg=self.colors['sidebar'], height=50)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            tk.Label(header, text=f"📄 {name}",
                    bg=self.colors['sidebar'], fg=self.colors['success'],
                    font=('Segoe UI', 14, 'bold'), anchor='w',
                    padx=20, pady=15).pack(side='left')
            
            info = tk.Label(header, 
                          text=f"Size: {file_item.size} bytes | Inode: {file_item.inode}",
                          bg=self.colors['sidebar'], fg=self.colors['text_dim'],
                          font=('Segoe UI', 9), anchor='w')
            info.pack(side='left', padx=20)
            
            content_frame = tk.Frame(viewer, bg=self.colors['panel'])
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            text_widget = scrolledtext.ScrolledText(content_frame,
                                                   bg=self.colors['bg'],
                                                   fg=self.colors['text'],
                                                   font=('Consolas', 10),
                                                   wrap='word',
                                                   relief='flat',
                                                   borderwidth=0)
            text_widget.pack(fill='both', expand=True)
            text_widget.insert('1.0', file_item.content)
            text_widget.config(state='disabled')
            
            self.update_stats()
        else:
            messagebox.showerror("Error", "Could not read file", parent=self.root)
    
    def edit_file(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to edit",
                                 parent=self.root)
            return
        
        item = self.tree.item(selection[0])
        name = item['text']
        
        if not name.startswith('📄'):
            messagebox.showwarning("Warning", "Please select a file",
                                 parent=self.root)
            return
        
        name = name[2:].strip()
        file_item = self.vfs.read_file(name)
        
        if file_item:
            editor = tk.Toplevel(self.root)
            editor.title(f"Edit: {name}")
            editor.geometry("700x500")
            editor.configure(bg=self.colors['bg'])
            
            header = tk.Frame(editor, bg=self.colors['sidebar'], height=50)
            header.pack(fill='x')
            header.pack_propagate(False)
            
            tk.Label(header, text=f"✏️ Editing: {name}",
                    bg=self.colors['sidebar'], fg=self.colors['success'],
                    font=('Segoe UI', 14, 'bold'), anchor='w',
                    padx=20, pady=15).pack(side='left')
            
            content_frame = tk.Frame(editor, bg=self.colors['panel'])
            content_frame.pack(fill='both', expand=True, padx=20, pady=(10, 0))
            
            text_widget = scrolledtext.ScrolledText(content_frame,
                                                   bg=self.colors['bg'],
                                                   fg=self.colors['text'],
                                                   font=('Consolas', 10),
                                                   wrap='word',
                                                   relief='flat',
                                                   borderwidth=0)
            text_widget.pack(fill='both', expand=True)
            text_widget.insert('1.0', file_item.content)
            
            def save_content():
                new_content = text_widget.get('1.0', 'end-1c')
                success, msg = self.vfs.write_file(name, new_content)
                if success:
                    messagebox.showinfo("Success", msg, parent=editor)
                    editor.destroy()
                    self.refresh_file_list()
                else:
                    messagebox.showerror("Error", msg, parent=editor)
            
            btn_frame = tk.Frame(editor, bg=self.colors['bg'])
            btn_frame.pack(fill='x', padx=20, pady=20)
            
            save_btn = tk.Button(btn_frame, text="💾 Save",
                               command=save_content,
                               bg=self.colors['success'], fg='white',
                               relief='flat', font=('Segoe UI', 10, 'bold'),
                               padx=30, pady=10, cursor='hand2')
            save_btn.pack(side='left', padx=5)
            
            cancel_btn = tk.Button(btn_frame, text="❌ Cancel",
                                  command=editor.destroy,
                                  bg=self.colors['error'], fg='white',
                                  relief='flat', font=('Segoe UI', 10),
                                  padx=30, pady=10, cursor='hand2')
            cancel_btn.pack(side='left', padx=5)
            
            self.update_stats()
        else:
            messagebox.showerror("Error", "Could not read file", parent=self.root)
    
    def clear_cache(self):
        self.vfs.clear_cache()
        messagebox.showinfo("Cache Cleared", 
                          "Dentry and Inode caches have been cleared!",
                          parent=self.root)
        self.update_stats()
        self.update_log()
    
    def change_filesystem(self, event=None):
        fs_type_str = self.fs_var.get()
        fs_type = FileSystemType(fs_type_str)
        
        if messagebox.askyesno("Change File System",
                              f"Mount {fs_type_str} file system?\nThis will reset the current file system.",
                              parent=self.root):
            self.vfs = VirtualFileSystem(fs_type)
            self.refresh_file_list()
            messagebox.showinfo("Success", 
                              f"Mounted {fs_type_str} file system successfully!",
                              parent=self.root)
    
    def show_architecture(self):
        arch_window = tk.Toplevel(self.root)
        arch_window.title("VFS Architecture")
        arch_window.geometry("900x700")
        arch_window.configure(bg=self.colors['bg'])
        
        header = tk.Frame(arch_window, bg=self.colors['sidebar'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="🏗️ Virtual File System Architecture",
                bg=self.colors['sidebar'], fg=self.colors['success'],
                font=('Segoe UI', 16, 'bold'), anchor='w',
                padx=20, pady=15).pack(side='left')
        
        content_frame = tk.Frame(arch_window, bg=self.colors['panel'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        arch_text = scrolledtext.ScrolledText(content_frame,
                                             bg=self.colors['bg'],
                                             fg=self.colors['text'],
                                             font=('Consolas', 10),
                                             wrap='word',
                                             relief='flat',
                                             borderwidth=0)
        arch_text.pack(fill='both', expand=True)
        
        architecture_info = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    VFS ARCHITECTURE LAYERS                                ║
╚══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│  1. USER SPACE                                                           │
│     └─ Applications make system calls: open(), read(), write(), close() │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  2. VFS LAYER (Virtual File System)                                     │
│     ├─ File Object Management                                           │
│     ├─ Dentry Cache (Directory Entry Cache)                             │
│     ├─ Inode Cache (Index Node Cache)                                   │
│     └─ System Call Interface                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  3. FILE SYSTEM TYPES                                                    │
│     ├─ ext4   (Linux Default File System)                               │
│     ├─ NTFS   (Windows File System)                                     │
│     ├─ FAT32  (Legacy/USB File System)                                  │
│     ├─ Btrfs  (Advanced Copy-on-Write FS)                               │
│     ├─ XFS    (High Performance FS)                                     │
│     └─ NFS    (Network File System)                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  4. BLOCK LAYER                                                          │
│     ├─ Block I/O Operations                                             │
│     ├─ I/O Scheduler (CFQ, Deadline, NOOP)                              │
│     └─ Request Queue Management                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  5. DEVICE DRIVERS                                                       │
│     ├─ SCSI Driver                                                      │
│     ├─ SATA Driver                                                      │
│     ├─ NVMe Driver                                                      │
│     └─ Network Driver                                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  6. HARDWARE LAYER                                                       │
│     ├─ Hard Disk Drive (HDD)                                            │
│     ├─ Solid State Drive (SSD)                                          │
│     └─ Network Storage (NAS/SAN)                                        │
└─────────────────────────────────────────────────────────────────────────┘


╔══════════════════════════════════════════════════════════════════════════╗
║                    KEY FEATURES IMPLEMENTED                               ║
╚══════════════════════════════════════════════════════════════════════════╝

✓ Multi-File System Support
  • Supports 6 different file system types
  • Easy switching between file systems
  • File system-specific operations logging

✓ Advanced Caching Mechanisms
  • Dentry Cache: Caches directory entries for faster lookups
  • Inode Cache: Caches file metadata for quick access
  • Cache hit/miss tracking with performance metrics

✓ Complete System Call Operations
  • CREATE  - Create files and directories
  • DELETE  - Remove files and directories (with safety checks)
  • READ    - Read file contents
  • WRITE   - Modify file contents
  • CHDIR   - Navigate directory structure
  • READDIR - List directory contents

✓ File System Management
  • Hierarchical directory structure
  • Inode-based file identification
  • Parent-child relationship tracking
  • Non-empty directory protection

✓ Performance Monitoring
  • Real-time operation logging
  • Cache performance statistics
  • Operation count tracking
  • Success/failure rate monitoring

✓ Modern GUI Interface
  • Intuitive file browser
  • Real-time statistics dashboard
  • Operation log viewer
  • File editor and viewer


╔══════════════════════════════════════════════════════════════════════════╗
║                    VFS ADVANTAGES                                         ║
╚══════════════════════════════════════════════════════════════════════════╝

1. ABSTRACTION
   Applications don't need to know the underlying file system type
   
2. PORTABILITY
   Same system calls work across different file systems
   
3. FLEXIBILITY
   Easy to add support for new file system types
   
4. PERFORMANCE
   Caching mechanisms improve access speed
   
5. CONSISTENCY
   Uniform interface for all file operations


╔══════════════════════════════════════════════════════════════════════════╗
║                    SYSTEM CALL FLOW EXAMPLE                               ║
╚══════════════════════════════════════════════════════════════════════════╝

Example: Reading a file (/home/user/readme.txt)

1. Application calls: open("/home/user/readme.txt", O_RDONLY)
   ↓
2. VFS checks dentry cache for path lookup
   ↓
3. VFS locates inode (checks inode cache)
   ↓
4. VFS creates file descriptor and file object
   ↓
5. Application calls: read(fd, buffer, size)
   ↓
6. VFS routes to specific FS implementation (ext4, NTFS, etc.)
   ↓
7. FS implementation reads data from block device
   ↓
8. Data returned to application through VFS layer


╔══════════════════════════════════════════════════════════════════════════╗
║                    DEVELOPED FOR VIRTUAL FILE STIMULATION                 ║
╚══════════════════════════════════════════════════════════════════════════╝

This simulator demonstrates:
• Deep understanding of VFS architecture
• System call implementation
• Caching strategies and performance optimization
• Modern GUI development with Python
• File system concepts and data structures
        """
        
        arch_text.insert('1.0', architecture_info)
        arch_text.config(state='disabled')
        
        close_btn = tk.Button(arch_window, text="Close",
                            command=arch_window.destroy,
                            bg=self.colors['accent'], fg='white',
                            relief='flat', font=('Segoe UI', 10),
                            padx=30, pady=10, cursor='hand2')
        close_btn.pack(pady=20)

def main():
    root = tk.Tk()
    app = VFSGuiApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()