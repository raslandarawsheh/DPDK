dnl Process this file with autoconf to produce a configure script.

AC_PREREQ(2.57)
AC_INIT(libmlx4, 1.0.5mlnx1, linux-rdma@vger.kernel.org)
AC_CONFIG_SRCDIR([src/mlx4.h])
AC_CONFIG_AUX_DIR(config)
AC_CONFIG_HEADER(config.h)
AM_INIT_AUTOMAKE([1.10 foreign tar-ustar silent-rules subdir-objects])
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_PROG_LIBTOOL
LT_INIT

AC_ARG_WITH([valgrind],
    AC_HELP_STRING([--with-valgrind],
        [Enable Valgrind annotations (small runtime overhead, default NO)]))
if test x$with_valgrind = x || test x$with_valgrind = xno; then
    want_valgrind=no
    AC_DEFINE([NVALGRIND], 1, [Define to 1 to disable Valgrind annotations.])
else
    want_valgrind=yes
    if test -d $with_valgrind; then
        CPPFLAGS="$CPPFLAGS -I$with_valgrind/include"
    fi
fi

AC_ARG_WITH([dpdk],
	AC_HELP_STRING([--with-dpdk],
		[Optimize library for DPDK applications [default=no]]))

AC_ARG_WITH([dpdk-inline-send],
	AC_HELP_STRING([--with-dpdk-inline-send],
		[Use inline send with DPDK [default=no]]))

AC_ARG_WITH([dpdk-inline-recv],
	AC_HELP_STRING([--with-dpdk-inline-recv],
		[Use inline recv with DPDK [default=no]]))

AC_ARG_WITH([dpdk-rx-csum],
	AC_HELP_STRING([--without-dpdk-rx-csum],
		[Disable recv checksum HW offload with DPDK [default=no]]))

if test x$with_dpdk = xyes; then
	AC_DEFINE([DPDK], 1, [Define to 1 to optimize for DPDK.])
	if test x$with_dpdk_inline_send = xyes; then
		AC_DEFINE([DPDK_INLINE_TX], 1, [Define to 1 to use inline send with DPDK.])
	fi
	if test x$with_dpdk_inline_recv = xyes; then
		AC_DEFINE([DPDK_INLINE_RX], 1, [Define to 1 to use inline receive with DPDK.])
	fi
	if test x$with_dpdk_rx_csum = xno; then
		AC_DEFINE([DPDK_RX_CSUM_DISABLED], 1, [Define to 1 to disable recv checksum HW offload with DPDK.])
	fi
fi

dnl Checks for programs
AC_PROG_CC

dnl Checks for libraries
AC_CHECK_LIB(ibverbs, ibv_get_device_list, [],
    AC_MSG_ERROR([ibv_get_device_list() not found.  libmlx4 requires libibverbs.]))

dnl Checks for header files.
AC_CHECK_HEADER(infiniband/driver.h, [],
    AC_MSG_ERROR([<infiniband/driver.h> not found.  libmlx4 requires libibverbs.]))
AC_HEADER_STDC
AS_IF([test x$want_valgrind = xyes],
    [AC_CHECK_HEADER([valgrind/memcheck.h],
        [AC_DEFINE(HAVE_VALGRIND_MEMCHECK_H, 1,
            [Define to 1 if you have the <valgrind/memcheck.h> header file.])],
        [AC_MSG_ERROR([Valgrind memcheck support requested, but <valgrind/memcheck.h> not found.])])])

dnl Checks for typedefs, structures, and compiler characteristics.
AC_C_CONST
AC_CHECK_SIZEOF(long)

dnl Checks for library functions
AC_CHECK_FUNC(ibv_read_sysfs_file, [],
    AC_MSG_ERROR([ibv_read_sysfs_file() not found.  libmlx4 requires libibverbs >= 1.0.3.]))
AC_CHECK_FUNCS(ibv_dontfork_range ibv_dofork_range ibv_register_driver)

dnl Now check if for libibverbs 1.0 vs 1.1
dummy=if$$
cat <<IBV_VERSION > $dummy.c
#include <infiniband/driver.h>
IBV_DEVICE_LIBRARY_EXTENSION
IBV_VERSION
IBV_DEVICE_LIBRARY_EXTENSION=`$CC $CPPFLAGS -E $dummy.c 2> /dev/null | tail -1`
rm -f $dummy.c
AM_CONDITIONAL(HAVE_IBV_DEVICE_LIBRARY_EXTENSION,
    test $IBV_DEVICE_LIBRARY_EXTENSION != IBV_DEVICE_LIBRARY_EXTENSION)
AC_SUBST(IBV_DEVICE_LIBRARY_EXTENSION)

AC_CACHE_CHECK(whether ld accepts --version-script, ac_cv_version_script,
    [if test -n "`$LD --help < /dev/null 2>/dev/null | grep version-script`"; then
        ac_cv_version_script=yes
    else
        ac_cv_version_script=no
    fi])

if test $ac_cv_version_script = yes; then
    MLX4_VERSION_SCRIPT='-Wl,--version-script=$(srcdir)/src/mlx4.map'
else
    MLX4_VERSION_SCRIPT=
fi
AC_SUBST(MLX4_VERSION_SCRIPT)

AC_CONFIG_FILES([Makefile libmlx4.spec])
AC_OUTPUT
