#define _GNU_SOURCE
#include <Python.h>
#include <sys/syscall.h>
#include <sys/mount.h>
#include <sched.h>
#include <sys/wait.h>
#include <unistd.h>

#define STACK_SIZE 32768

#define LINUX_MODULE_DOC "linux\n"\
                         "=====\n"\
                         "linux 模块是一个简单的 Python C extension，包含 Python os 模块缺失的 "\
                         "syscall wrappers。你需要在工作坊中使用这些 system calls "\
                         "实现 process containment 的不同方面。"

#define PIVOT_ROOT_DOC  ".. py:function:: pivot_root(new_root, put_old)\n"\
                        "\n"\
                        "修改 root filesystem\n"\
                        "\n"\
                        ":param str new_root: 新的 root file system\n"\
                        ":param str put_old: 用于移动当前 process root file system 的目录\n"\
                        ":return: None\n"\
                        ":raises RuntimeError: pivot_root 失败时抛出\n"\
                        "\n"\
                        "**注意：** 以下限制适用于 `new_root` 和 `put_old`：\n"\
                        "\n"\
                        "* 它们必须是目录。\n"\
                        "* `new_root` 和 put_old 不能与当前 root 位于同一个 filesystem。\n"\
                        "* `new_root` 必须是 mountpoint。\n"\
                        "* `put_old` 必须位于 `new_root` 之下，也就是说，在 `put_old` 指向的字符串后\n"\
                        "  添加非零数量的 /.. 后，必须能得到和 `new_root` 相同的目录。\n"\
                        "* `put_old` 上不能 mount 其他 filesystem。\n"

static PyObject *
pivot_root(PyObject *self, PyObject *args) {
	const char *put_old, *new_root;

	if (!PyArg_ParseTuple(args, "ss", &new_root, &put_old))
		return NULL;

	if (syscall(SYS_pivot_root, new_root, put_old) == -1) {
		PyErr_SetFromErrno(PyExc_RuntimeError);
		return NULL;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

#define MOUNT_DOC   ".. py:function:: mount(source, target, filesystemtype, mountflags, mountopts)\n"\
                    "\n"\
                    "mount filesystem\n"\
                    "\n"\
                    ":param str source: 要挂接的 filesystem（可以是 ``None``）\n"\
                    ":param str target: 要挂接到的目录，或要操作的目录（修改 flag 时）\n"\
                    ":param str filesystemtype: kernel 支持的 filesystem（可以是 ``None``）\n"\
                    ":param int mountflags: mount(2) 支持的 mount flags 的任意组合（使用 ``|``）。\n"\
                    "                       在工作坊中，你最可能使用 ``0``（即无 flags），\n"\
                    "                       或这些值的组合：``linux.MS_REC``、``linux.MS_PRIVATE``\n"\
                    ":param str mountopts: 传给指定 filesystem 的 options（可以是 ``None``）\n"\
                    ":return: None\n"\
                    ":raises RuntimeError: mount 失败时抛出\n"\
                    "\n"

static PyObject *
_mount(PyObject *self, PyObject *args) {
	const char *source, *target, *filesystemtype, *mountopts;
	unsigned long mountflags;

	if (!PyArg_ParseTuple(args, "zszkz", &source, &target, &filesystemtype, &mountflags, &mountopts)) {
		return NULL;
	}

	if (mount(source, target, filesystemtype, mountflags, mountopts) == -1) {
		PyErr_SetFromErrno(PyExc_RuntimeError);
		return NULL;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

#define UMOUNT_DOC  ".. py:function:: umount(target)\n"\
                    "\n"\
                    "unmount filesystem\n"\
                    "\n"\
                    ":param str target: 该目录所在的（最顶层）filesystem 会被移除\n"\
                    ":return: None\n"\
                    ":raises RuntimeError: umount 失败时抛出\n"\
                    "\n"

static PyObject *
_umount(PyObject *self, PyObject *args) {
	const char *target;

	if (!PyArg_ParseTuple(args, "s", &target)) {
		return NULL;
	}

	if (umount(target) == -1) {
		PyErr_SetFromErrno(PyExc_RuntimeError);
		return NULL;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

#define UMOUNT2_DOC  ".. py:function:: umount2(target, flags)\n"\
                    "\n"\
                    "unmount filesystem，但允许使用额外 `flags` 控制操作行为\n"\
                    "\n"\
                    ":param str target: 该目录所在的（最顶层）filesystem 会被移除\n"\
                    ":param int flags: 控制操作行为。可以使用 ``|`` 组合多个 flags。\n"\
                    "                  在工作坊中，你最可能使用\n"\
                    "                  ``linux.MNT_DETACH``\n"\
                    ":return: None\n"\
                    ":raises RuntimeError: umount2 失败时抛出\n"\
                    "\n"

static PyObject *
_umount2(PyObject *self, PyObject *args) {
	const char *target;
	int flags;

	if (!PyArg_ParseTuple(args, "si", &target, &flags)) {
		return NULL;
	}

	if (umount2(target, flags) == -1) {
		PyErr_SetFromErrno(PyExc_RuntimeError);
		return NULL;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

#define UNSHARE_DOC ".. py:function:: unshare(flags)\n"\
                    "\n"\
                    "解除 process execution context 中部分内容的关联\n"\
                    "\n"\
                    ":param int flags: execution context 中哪些部分需要 unshare。你可以\n"\
                    "                  使用 ``|`` 组合多个 flags。下面列出了你在\n"\
                    "                  工作坊中可能会用到的 flags\n"\
                    ":return: None\n"\
                    ":raises RuntimeError: unshare 失败时抛出\n"\
                    "\n"\
                    "常用 flags：\n"\
                    "\n"\
                    "* ``linux.CLONE_NEWNS`` - Unshare mount namespace\n"\
                    "* ``linux.CLONE_NEWUTS`` - Unshare UTS namespace（hostname、domainname 等）\n"\
                    "* ``linux.CLONE_NEWNET`` - Unshare network namespace\n"\
                    "* ``linux.CLONE_NEWPID`` - Unshare PID namespace\n"\

static PyObject *
_unshare(PyObject *self, PyObject *args) {
	int clone_flags;

	if (!PyArg_ParseTuple(args, "i", &clone_flags))
		return NULL;

	if (unshare(clone_flags) == -1) {
		PyErr_SetFromErrno(PyExc_RuntimeError);
		return NULL;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

#define SETNS_DOC   ".. py:function:: setns(fd, nstype)\n"\
                    "\n"\
                    "把 process 重新关联到某个 namespace\n"\
                    "\n"\
                    ":param int fd: 指向要关联 namespace 的 file descriptor\n"\
                    ":param int nstype: 下列值之一：``0``（允许加入任意类型的 namespace）、\n"\
                    "                   ``CLONE_NEWIPC``（加入 IPC namespace）、``CLONE_NEWNET``（加入 network\n"\
                    "                   namespace），或 ``CLONE_NEWUTS``（加入 UTS namespace）\n"\
                    ":return: None\n"\
                    ":raises RuntimeError: setns 失败时抛出\n"\
                    "\n"\

static PyObject *
_setns(PyObject *self, PyObject *args) {
	int fd, nstype;

	if (!PyArg_ParseTuple(args, "ii", &fd, &nstype))
		return NULL;

	if (setns(fd, nstype) == -1) {
		PyErr_SetFromErrno(PyExc_RuntimeError);
		return NULL;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

struct py_clone_args {
	PyObject *callback;
	PyObject *callback_args;
};

static int clone_callback(void *args) {
	PyObject *result;
	struct py_clone_args *call_args = (struct py_clone_args *)args;

	if ((result = PyObject_CallObject(call_args->callback, call_args->callback_args)) == NULL) {
		PyErr_Print();
		return -1;
	} else {
		Py_DECREF(result);
	}
	return 0;
}

#define CLONE_DOC   ".. py:function:: clone(callback, flags, callback_args)\n"\
                    "\n"\
                    "创建 child process\n"\
                    "\n"\
                    ":param Callable callback: 由 fork 出来的 child 执行的 Python function\n"\
                    ":param int flags: flags 的组合（使用 ``|``），指定 calling process 和 child process\n"\
                    "                  之间应共享什么。见下文。\n"\
                    ":param tuple callback_args: callback function 的参数 tuple\n"\
                    ":return: 成功时返回 child process 的 thread ID\n"\
                    ":raises RuntimeError: clone 失败时抛出\n"\
                    "\n"\
                    "\n"\
                    "常用 flags：\n"\
                    "\n"\
                    "* ``linux.CLONE_NEWNS`` - Unshare mount namespace\n"\
                    "* ``linux.CLONE_NEWUTS`` - Unshare UTS namespace（hostname、domainname 等）\n"\
                    "* ``linux.CLONE_NEWNET`` - Unshare network namespace\n"\
                    "* ``linux.CLONE_NEWPID`` - Unshare PID namespace\n"\

static PyObject *
_clone(PyObject *self, PyObject *args) {
	PyObject *callback, *callback_args;
	void *child_stack;
	int flags;
	pid_t child_pid;

	child_stack = malloc(STACK_SIZE);

	if (!PyArg_ParseTuple(args, "OiO", &callback, &flags, &callback_args))
		return NULL;

	if (!PyCallable_Check(callback)) {
		PyErr_SetString(PyExc_TypeError, "parameter must be callable");
        return NULL;
    }

    struct py_clone_args call_args;
    call_args.callback = callback;
    call_args.callback_args = callback_args;

	if ((child_pid = clone(&clone_callback, child_stack + STACK_SIZE, flags | SIGCHLD, &call_args)) == -1) {
			PyErr_SetFromErrno(PyExc_RuntimeError);
			return Py_BuildValue("i", -1);
	} else {
		return Py_BuildValue("i", child_pid);
	}
}

#define SETHOSTNAME_DOC ".. py:function:: sethostname(hostname)\n"\
                        "\n"\
                        "设置 system hostname\n"\
                        "\n"\
                        ":param str hostname: 新的 hostname 值\n"\
                        ":return: None\n"\
                        ":raises RuntimeError: sethostname 失败时抛出\n"\
                        "\n"\

static PyObject *
_sethostname(PyObject *self, PyObject *args) {
	const char *hostname;

	if (!PyArg_ParseTuple(args, "s", &hostname))
		return NULL;

	if (sethostname(hostname, strlen(hostname)) == -1) {
		PyErr_SetFromErrno(PyExc_RuntimeError);
		return NULL;
	}

	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef LinuxMethods[] = {
	{"pivot_root", pivot_root, METH_VARARGS, PIVOT_ROOT_DOC},
	{"unshare", _unshare, METH_VARARGS, UNSHARE_DOC},
	{"setns", _setns, METH_VARARGS, SETNS_DOC},
	{"clone", _clone, METH_VARARGS, CLONE_DOC},
	{"sethostname", _sethostname, METH_VARARGS, SETHOSTNAME_DOC},
	{"mount", _mount, METH_VARARGS, MOUNT_DOC},
	{"umount", _umount, METH_VARARGS, UMOUNT_DOC},
	{"umount2", _umount2, METH_VARARGS, UMOUNT2_DOC},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef linuxmodule = {
	PyModuleDef_HEAD_INIT,
	"linux",
	LINUX_MODULE_DOC,
	-1,
	LinuxMethods
};

PyMODINIT_FUNC
PyInit_linux(void)
{
	PyObject *module = PyModule_Create(&linuxmodule);


	// clone 常量
	PyModule_AddIntConstant(module, "CLONE_NEWNS", CLONE_NEWNS);     // mount namespace
	PyModule_AddIntConstant(module, "CLONE_NEWUTS", CLONE_NEWUTS);   // UTS (hostname) namespace
	PyModule_AddIntConstant(module, "CLONE_NEWPID", CLONE_NEWPID);   // PID namespace
	PyModule_AddIntConstant(module, "CLONE_NEWUSER", CLONE_NEWUSER); // users namespace
	PyModule_AddIntConstant(module, "CLONE_NEWIPC", CLONE_NEWIPC);   // IPC namespace
	PyModule_AddIntConstant(module, "CLONE_NEWNET", CLONE_NEWNET);   // network namespace
	PyModule_AddIntConstant(module, "CLONE_THREAD", CLONE_THREAD);

	// mount 常量
	PyModule_AddIntConstant(module, "MS_RDONLY", MS_RDONLY);               /* Mount read-only.  */
	PyModule_AddIntConstant(module, "MS_NOSUID", MS_NOSUID);               /* Ignore suid and sgid bits.  */
	PyModule_AddIntConstant(module, "MS_NODEV", MS_NODEV);                 /* Disallow access to device special files.  */
	PyModule_AddIntConstant(module, "MS_NOEXEC", MS_NOEXEC);               /* Disallow program execution.  */
	PyModule_AddIntConstant(module, "MS_SYNCHRONOUS", MS_SYNCHRONOUS);     /* Writes are synced at once.  */
	PyModule_AddIntConstant(module, "MS_REMOUNT", MS_REMOUNT);             /* Alter flags of a mounted FS.  */
	PyModule_AddIntConstant(module, "MS_MANDLOCK", MS_MANDLOCK);           /* Allow mandatory locks on an FS.  */
	PyModule_AddIntConstant(module, "MS_DIRSYNC", MS_DIRSYNC);             /* Directory modifications are synchronous.  */
	PyModule_AddIntConstant(module, "MS_NOATIME", MS_NOATIME);             /* Do not update access times.  */
	PyModule_AddIntConstant(module, "MS_NODIRATIME", MS_NODIRATIME);       /* Do not update directory access times.  */
	PyModule_AddIntConstant(module, "MS_BIND", MS_BIND);                   /* Bind directory at different place.  */
	PyModule_AddIntConstant(module, "MS_MOVE", MS_MOVE);
	PyModule_AddIntConstant(module, "MS_REC", MS_REC);                     /* Recursive loopback */
	PyModule_AddIntConstant(module, "MS_SILENT", MS_SILENT);
	PyModule_AddIntConstant(module, "MS_POSIXACL", MS_POSIXACL);           /* VFS does not apply the umask.  */
	PyModule_AddIntConstant(module, "MS_UNBINDABLE", MS_UNBINDABLE);       /* Change to unbindable.  */
	PyModule_AddIntConstant(module, "MS_PRIVATE", MS_PRIVATE);             /* Change to private.  */
	PyModule_AddIntConstant(module, "MS_SLAVE", MS_SLAVE);                 /* Change to slave.  */
	PyModule_AddIntConstant(module, "MS_SHARED", MS_SHARED);               /* Change to shared.  */
	PyModule_AddIntConstant(module, "MS_RELATIME", MS_RELATIME);           /* Update atime relative to mtime/ctime.  */
	PyModule_AddIntConstant(module, "MS_KERNMOUNT", MS_KERNMOUNT);         /* This is a kern_mount call.  */
	PyModule_AddIntConstant(module, "MS_I_VERSION", MS_I_VERSION);         /* Update inode I_version field.  */
	PyModule_AddIntConstant(module, "MS_STRICTATIME", MS_STRICTATIME);     /* Always perform atime updates.  */
	PyModule_AddIntConstant(module, "MS_ACTIVE", MS_ACTIVE);
	PyModule_AddIntConstant(module, "MS_NOUSER", MS_NOUSER);
	PyModule_AddIntConstant(module, "MNT_DETACH", MNT_DETACH);             /* Just detach from the tree.  */
	PyModule_AddIntConstant(module, "MS_MGC_VAL", MS_MGC_VAL);
	
	return module;
}
