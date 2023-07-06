# 文件IO

文件I/O是操作系统不可或缺的部分，也是实现数据持久化的手段。对于Linux来说，其“一切皆是文件”的思想，更是突出了文件在Linux内核中的重要地位。

## Linux中的文件

### 文件、文件描述符和文件表

Linux内核将一切视为文件，那么Linux的文件是什么呢？其既可以是事实上的真正的物理文件，也可以是设备、管道，甚至还可以是一块内存。

狭义的文件是指文件系统中的物理文件，而广义的文件则可以是Linux管理的所有对象。这些广义的文件利用VFS机制，以文件系统的形式挂载在Linux内核中，对外提供一致的文件操作接口。

**文件描述符**: 从数值上看，文件描述符是一个非负整数，其本质就是一个**句柄**，所以也可以认为文件描述符就是一个文件句柄。一切对于用户透明的返回值，即可视为句柄。用户空间利用文件描述符与内核进行交互；而内核拿到文件描述符后，可以通过它得到用于管理文件的真正的数据结构。

使用文件描述符，有两个好处：

1. 一是增加了安全性，句柄类型对用户完全透明，用户无法通过任何hacking的方式，更改句柄对应的内部结果，比如Linux内核的文件描述符，只有内核才能通过该值得到对应的文件结构；
2. 二是增加了可扩展性，用户的代码只依赖于句柄的值，这样实际结构的类型就可以随时发生变化，与句柄的映射关系也可以随时改变，这些变化都不会影响任何现有的用户代码。

**文件表**: Linux的每个进程都会维护一个文件表，以便维护该进程打开文件的信息，包括打开的文件个数、每个打开文件的偏移量等信息。

### 内核文件的表现

内核中进程对应的结构是task_struct，进程的文件表保存在task_struct->files中。

```c
struct files_struct {
    /* count为文件表files_struct的引用计数 */
    atomic_t count;
    /* 文件描述符表 */
    /*
     为什么有两个fdtable呢？这是内核的一种优化策略。fdt为指针，而fdtab为普通变量。一般情况下，
     fdt是指向fdtab的，当需要它的时候，才会真正动态申请内存。因为默认大小的文件表足以应付大多数情况，因此这样就可以避免频繁的内存申请。这也是内核的常用技巧之一。在创建时，使用普通的变量或者数组，然后让指针指向它，作为默认情况使用。只有当进程使用量超过默认值时，才会动态申请内存。
    */
    struct fdtable __rcu *fdt;
    struct fdtable fdtab;
    /*
    * written part on a separate cache line in SMP
    */
    /* 使用____cacheline_aligned_in_smp可以保证file_lock是以cache
     line 对齐的，避免了false sharing */
    spinlock_t file_lock ____cacheline_aligned_in_smp;
    /* 用于查找下一个空闲的fd */
    int next_fd;
    /* 保存执行exec需要关闭的文件描述符的位图 */
    struct embedded_fd_set close_on_exec_init;
    /* 保存打开的文件描述符的位图 */
    struct embedded_fd_set open_fds_init;
    /* fd_array为一个固定大小的file结构数组。struct file是内核用于文件管理的结构。这里使用默认大小的数组，就是为了可以涵盖大多数情况，避免动态分配 */
    struct file __rcu * fd_array[NR_OPEN_DEFAULT];
};
```

## 打开文件

### open介绍

open在手册中有两个函数原型，如下所示：

```c
int open(const char *pathname, int flags);￼
int open(const char *pathname, int flags, mode_t mode);
```

这样的函数原型有些违背了我们的直觉。C语言是不支持函数重载的，为什么open的系统调用可以有两个这样的open原型呢？

- 在Linux内核中，实际上只提供了一个系统调用，对应的是上述两个函数原型中的第二个。

- 当调用open函数时，实际上调用的是glibc封装的函数，然后由glibc通过自陷指令，进行真正的系统调用。也就是说，所有的系统调用都要先经过glibc才会进入操作系统。这样的话，实际上是glibc提供了一个变参函数open来满足两个函数原型，然后通过glibc的变参函数open实现真正的系统调用来调用原型二。

open的参数：

- pathname：表示要打开的文件路径。
- flags：用于指示打开文件的选项，常用的有O_RDONLY、O_WRONLY和O_RDWR。这三个选项必须有且只能有一个被指定。为什么O_RDWR！=O_RDONLY|O_WRONLY呢？Linux环境中，O_RDONLY被定义为0，O_WRONLY被定义为1，而O_RDWR却被定义为2。之所以有这样违反常规的设计遗留至今，就是为了兼容以前的程序。除了以上三个选项，Linux平台还支持更多的选项。
- mode：只在创建文件时需要，用于指定所创建文件的权限位（还要受到umask环境变量的影响）。

### 更多选项

- O_APPEND：每次进行写操作时，内核都会先定位到文件尾，再执行写操作。

- O_ASYNC：使用异步I/O模式。

- **O_CLOEXEC**：在打开文件的时候，就为文件描述符设置FD_CLOEXEC标志。这是一个新的选项，用于解决在多线程下fork与用fcntl设置FD_CLOEXEC的竞争问题。某些应用使用fork来执行第三方的业务，为了避免泄露已打开文件的内容，那些文件会设置FD_CLOEXEC标志。但是fork与fcntl是两次调用，在多线程下，可能会在fcntl调用前，就已经fork出子进程了，从而导致该文件句柄暴露给子进程。关于O_CLOEXEC的用途，将会在第4章详细讲解。

- O_CREAT：当文件不存在时，就创建文件。

- O_DIRECT：对该文件进行直接I/O，不使用VFS Cache。

- O_DIRECTORY：要求打开的路径必须是目录。

- O_EXCL：该标志用于确保是此次调用创建的文件，需要与O_CREAT同时使用；当文件已经存在时，open函数会返回失败。

- O_LARGEFILE：表明文件为大文件。

- O_NOATIME：读取文件时，不更新文件最后的访问时间。

- O_NONBLOCK、O_NDELAY：将该文件描述符设置为非阻塞的（默认都是阻塞的）。

- O_SYNC：设置为I/O同步模式，每次进行写操作时都会将数据同步到磁盘，然后write才能返回。

- **O_TRUNC**：在打开文件的时候，将文件长度截断为0，需要与O_RDWR或O_WRONLY同时使用。在写文件时，如果是作为新文件重新写入，一定要使用O_TRUNC标志，否则可能会造成旧内容依然存在于文件中的错误，如生成配置文件、pid文件等

> 注意　并不是所有的文件系统都支持以上选项。

### open源码跟踪

跟踪内核open源码open->do_sys_open，代码如下：

```c
long do_sys_open(int dfd, const char __user *filename, int flags, int mode)
{
    struct open_flags op;
    /* flags为用户层传递的参数，内核会对flags进行合法性检查，并根据mode生成新的flags值赋给
      lookup */
    int lookup = build_open_flags(flags, mode, &op);
    /* 将用户空间的文件名参数复制到内核空间 */
    char *tmp = getname(filename);
    int fd = PTR_ERR(tmp);
    if (!IS_ERR(tmp)) {
        /* 未出错则申请新的文件描述符 */
        fd = get_unused_fd_flags(flags);
        if (fd >= 0) {
            /* 申请新的文件管理结构file */
            struct file *f = do_filp_open(dfd, tmp, &op, lookup);
            if (IS_ERR(f)) {
                put_unused_fd(fd);
                fd = PTR_ERR(f);
            } else {
                /* 产生文件打开的通知事件 */
                fsnotify_open(f);
                /* 将文件描述符fd与文件管理结构file对应起来，即安装 */
                fd_install(fd, f);
            }
        }
        putname(tmp);
    }
    return fd;
}
```

从do_sys_open可以看出，打开文件时，内核主要消耗了两种资源：文件描述符与内核管理文件结构file。

###  如何选择文件描述符

根据POSIX标准，当获取一个新的文件描述符时，要返回最低的未使用的文件描述符。Linux是如何实现这一标准的呢？

- 在Linux中，通过do_sys_open->get_unused_fd_flags->alloc_fd（0，（flags））来选择文件描述符。

```c
int alloc_fd(unsigned start, unsigned flags)
{
    struct files_struct *files = current->files;
    unsigned int fd;
    int error;
    struct fdtable *fdt;
    /* files为进程的文件表，下面需要更改文件表，所以需要先锁文件表 */
    spin_lock(&files->file_lock);
repeat:
    /* 得到文件描述符表 */
    fdt = files_fdtable(files);
    /* 从start开始，查找未用的文件描述符。在打开文件时，start为0 */
    fd = start;
    /* files->next_fd为上一次成功找到的fd的下一个描述符。使用next_fd，可以快速找到未用的文件描述符；*/
    if (fd < files->next_fd)
        fd = files->next_fd;
    /*
    当小于当前文件表支持的最大文件描述符个数时，利用位图找到未用的文件描述符。如果大于max_fds怎么办呢？如果大于当前支持的最大文件描述符，那它肯定是未用的，就不需要用位图来确认了。
    */
    if (fd < fdt->max_fds)
        fd = find_next_zero_bit(fdt->open_fds->fds_bits,
            fdt->max_fds, fd);
    /* expand_files用于在必要时扩展文件表。何时是必要的时候呢？比如当前文件描述符已经超过了当前文件表支持的最大值的时候。 */
    error = expand_files(files, fd);
    if (error < 0)
        goto out;
    /*
    * If we needed to expand the fs array we
    * might have blocked - try again.
    */
    if (error)
        goto repeat;
    /* 只有在start小于next_fd时，才需要更新next_fd，以尽量保证文件描述符的连续性。*/
    if (start <= files->next_fd)
        files->next_fd = fd + 1;
    /* 将打开文件位图open_fds对应fd的位置置位 */
    FD_SET(fd, fdt->open_fds);
    /* 根据flags是否设置了O_CLOEXEC，设置或清除fdt->close_on_exec */
    if (flags & O_CLOEXEC)
        FD_SET(fd, fdt->close_on_exec);
    else
        FD_CLR(fd, fdt->close_on_exec);
    error = fd;
#if 1
    /* Sanity check */
    if (rcu_dereference_raw(fdt->fd[fd]) != NULL) {
        printk(KERN_WARNING "alloc_fd: slot %d not NULL!\n", fd);
        rcu_assign_pointer(fdt->fd[fd], NULL);
    }
#endif
out:
    spin_unlock(&files->file_lock);
    return error;
}
```

### 文件描述符fd与文件管理结构file

当用户使用fd与内核交互时，内核可以用fd从fdt->fd[fd]中得到内部管理文件的结构struct file。

## creat简介

creat函数用于创建一个新文件，其等价于open（pathname，O_WRONLY|O_CREAT|O_TRUNC，mode）

creat无非是open的一种封装实现。

## 关闭文件

close用于关闭文件描述符。而文件描述符可以是普通文件，也可以是设备，还可以是socket。在关闭时，VFS会根据不同的文件类型，执行不同的操作。

### 　close介绍

close用于关闭文件描述符。而文件描述符可以是普通文件，也可以是设备，还可以是socket。在关闭时，VFS会根据不同的文件类型，执行不同的操作。

### close源码跟踪

Linux文件描述符选择策略：

- Linux选择文件描述符是按从小到大的顺序进行寻找的，文件表中next_fd用于记录下一次开始寻找的起点。当有空闲的描述符时，即可分配。
- 当某个文件描述符关闭时，如果其小于next_fd，则next_fd就重置为这个描述符，这样下一次分配就会立刻重用这个文件描述符。

以上的策略，总结成一句话就是“Linux文件描述符策略永远选择最小的可用的文件描述符”。——这也是POSIX标准规定的。

从`__put_unused_fd`退出后，close会接着调用filp_close，其调用路径为filp_close->fput。在fput中，会对当前文件struct file的引用计数减一并检查其值是否为0。当引用计数为0时，表示该struct file没有被其他人使用，则可以调用`__fput`执行真正的文件释放操作，然后调用要关闭文件所属文件系统的release函数，从而实现针对不同的文件类型来执行不同的关闭操作。

### 遗忘close造成的问题

遗忘close会带来什么样的后果:

- 文件描述符始终没有被释放。
- 用于文件管理的某些内存结构没有被释放。

对于普通进程来说，即使应用忘记了关闭文件，当进程退出时，Linux内核也会自动关闭文件，释放内存（详细过程见后文）。但是对于一个常驻进程来说，问题就变得严重了。

如果文件描述符没有被释放，那么再次申请新的描述符时，就不得不扩展当前的文件表了，代码如下：

```c
int expand_files(struct files_struct *files, int nr)
{
    struct fdtable *fdt;
    fdt = files_fdtable(files);
    /*
     * N.B. For clone tasks sharing a files structure, this test
     * will limit the total number of files that can be opened.
     */
    if (nr >= rlimit(RLIMIT_NOFILE))
        return -EMFILE;
    /* Do we need to expand? */
    if (nr < fdt->max_fds)
    return 0;
    /* Can we expand? */
    if (nr >= sysctl_nr_open)
    return -EMFILE;
    /* All good, so we try */
    return expand_fdtable(files, nr);
}
```

在扩展文件表的时候，会检查打开文件的个数是否超出系统的限制。如果文件描述符始终不释放，其个数迟早会到达上限，并返回EMFILE错误（表示Too many open files（POSIX.1））。

再看第二种情况，即文件管理的某些内存结构没有被释放。仍然是查看打开文件的代码，代码如下其中，get_empty_filp用于获得空闲的file结构：

```c
struct file *get_empty_filp(void)
{
    const struct cred *cred = current_cred();
    static long old_max;
    struct file * f;
    /*
     * Privileged users can go above max_files
     */
    /* 这里对打开文件的个数进行检查，非特权用户不能超过系统的限制 */
    if (get_nr_files() >= files_stat.max_files && !capable(CAP_SYS_ADMIN)) {
    /*
    再次检查per cpu的文件个数的总和，为什么要做两次检查呢。后文会详细介绍 */
    if (percpu_counter_sum_positive(&nr_files) >= files_stat.max_files)
        goto over;
    }
    /* 未到达上限，申请一个新的file结构 */
    f = kmem_cache_zalloc(filp_cachep, GFP_KERNEL);
    if (f == NULL)
        goto fail;
    /* 增加file结构计数 */
    percpu_counter_inc(&nr_files);
    f->f_cred = get_cred(cred);
    if (security_file_alloc(f))
        goto fail_sec;
    INIT_LIST_HEAD(&f->f_u.fu_list);
    atomic_long_set(&f->f_count, 1);
    rwlock_init(&f->f_owner.lock);
    spin_lock_init(&f->f_lock);
    eventpoll_init_file(f);
    /* f->f_version: 0 */
    return f;
over:
    /* 用完了file配额，打印log报错 */
    /* Ran out of filps - report that */
    if (get_nr_files() > old_max) {
        pr_info("VFS: file-max limit %lu reached\n", get_max_files());
        old_max = get_nr_files();
    }
    goto fail;
fail_sec:
    file_free(f);
fail:
    return NULL;
}
```

对于file的个数，Linux内核使用两种方式来计数。一是使用全局变量，另外一个是使用percpu变量。更新全局变量时，为了避免竞争，不得不使用锁，所以Linux使用了一种折中的解决方案。当percpu变量的个数变化不超过正负percpu_counter_batch（默认为32）的范围时，就不更新全局变量。这样就减少了对全局变量的更新，可是也造成了全局变量的值不准确的问题。于是在全局变量的file个数超过限制时，会再对所有的percpu变量求和，再次与系统的限制相比较。想了解这个计数手段的详细信息，可以阅读percpu_counter_add的相关代码。

### 如何查找文件资源泄漏

```sh
lsof -p [pid] # 查看进程打开文件
```

## 文件数据的同步

为了提高性能，操作系统会对文件的I/O操作进行缓存处理。对于读操作，如果要读取的内容已经存在于文件缓存中，就直接读取文件缓存。对于写操作，会先将修改提交到文件缓存中，在合适的时机或者过一段时间后，操作系统才会将改动提交到磁盘上。

Linux提供了三个同步接口：

```c
void sync(void);
int fsync(int fd);
int fdatasync(int fd);
```

对于sync函数，Linux手册上则表示从1.3.20版本开始，Linux就会一直等待，直到提交工作完成。

从sync的代码实现上看，Linux的sync是阻塞调用。

fsync只同步fd指定的文件，并且直到同步完成才返回。fdatasync与fsync类似，但是其只同步文件的实际数据内容，和会影响后面数据操作的元数据。而fsync不仅同步数据，还会同步所有被修改过的文件元数据。

从代码可以看出，fdatasync的性能会优于fsync。在不需要同步所有元数据的情况下，选择fdatasync会得到更好的性能。只有在inode被设置了I_DIRTY_DATASYNC标志时，fdatasync才需要同步inode的元数据。

那么inode何时会被设置I_DIRTY_DATASYNC这个标志呢？比如使用文件截断truncate或ftruncate时；通过在源码中搜索I_DIRTY_DATASYNC或mark_inode_dirty时也会给inode设置该标志位。而调用mark_inode_dirty的地方就太多了，这里就不一一列举了。

> sync、fsync和fdatasync只能保证Linux内核对文件的缓冲被冲刷了，并不能保证数据被真正写到磁盘上，因为磁盘也有自己的缓存。

## 文件的元数据

文件的元数据包括文件的访问权限、上次访问的时间戳、所有者、所有组、文件大小等信息。

### 获取文件的元数据

Linux环境提供了三个获取文件信息的API：

```c
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
int stat(const char *path, struct stat *buf);
int fstat(int fd, struct stat *buf);
int lstat(const char *path, struct stat *buf);
```

这三个函数都可用于得到文件的基本信息，区别在于stat得到路径path所指定的文件基本信息，fstat得到文件描述符fd指定文件的基本信息，而lstat与stat则基本相同，只有当path是一个链接文件时，lstat得到的是链接文件自己本身的基本信息而不是其指向文件的信息。

所得到的文件基本信息的结果struct stat的结构如下:

```c
struct stat {
     dev_t     st_dev;     /* ID of device containing file */
     ino_t     st_ino;     /* inode number */
     mode_t    st_mode;    /* protection */
     nlink_t   st_nlink;   /* number of hard links */
     uid_t     st_uid;     /* user ID of owner */
     gid_t     st_gid;     /* group ID of owner */
     dev_t     st_rdev;    /* device ID (if special file) */
     off_t     st_size;    /* total size, in bytes */
     blksize_t st_blksize; /* blocksize for file system I/O */
     blkcnt_t  st_blocks;  /* number of 512B blocks allocated */
     time_t    st_atime;   /* time of last access */
     time_t    st_mtime;   /* time of last modification */
     time_t    st_ctime;   /* time of last status change */
};
```

Linux的man手册对stat的各个变量做了注释，明确指出了每个变量的意义。唯一需要说明的是st_mode，其不仅仅是注释所说的“protection”，即权限管理，同时也用于表示文件类型，比如是普通文件还是目录。

### 内核如何维护文件的元数据

所有的文件元数据均保存在inode中，而inode是Linux也是所有类Unix文件系统中的一个概念。这样的文件系统一般将存储区域分为两类，一类是保存文件对象的元信息数据，即inode表；另一类是真正保存文件数据内容的块，所有inode完全由文件系统来维护。但是Linux也可以挂载非类Unix的文件系统，这些文件系统本身没有inode的概念，怎么办？Linux为了让VFS有统一的处理流程和方法，就必须要求那些没有inode概念的文件系统，根据自己系统的特点——如何维护文件元数据，生成“虚拟的”inode以供Linux内核使用。

### 权限位解析

在Linux环境中，文件常见的权限位有r、w和x，分别表示可读、可写和可执行。下面重点解析三个不常用的标志位。

#### 1.SUID权限位

当文件设置SUID权限位时，就意味着无论是谁执行这个文件，都会拥有该文件所有者的权限。passwd命令正是利用这个特性，来允许普通用户修改自己的密码，因为只有root用户才有修改密码文件的权限。当普通用户执行passwd命令时，就具有了root权限，从而可以修改自己的密码。

#### 2.SGID权限位

SGID与SUID权限位类似，当设置该权限位时，就意味着无论是谁执行该文件，都会拥有该文件所有者所在组的权限。

#### 3.Stricky位

Stricky位只有配置在目录上才有意义。当目录配置上sticky位时，其效果是即使所有的用户都拥有写权限和执行权限，该目录下的文件也只能被root或文件所有者删除。

