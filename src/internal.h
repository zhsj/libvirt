/*
 * internal.h: internal definitions just used by code from the library
 */

#ifndef __VIR_INTERNAL_H__
#define __VIR_INTERNAL_H__

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

#include "hash.h"
#include "libvir.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * ATTRIBUTE_UNUSED:
 *
 * Macro to flag conciously unused parameters to functions
 */
#ifdef __GNUC__
#ifdef HAVE_ANSIDECL_H
#include <ansidecl.h>
#endif
#ifndef ATTRIBUTE_UNUSED
#define ATTRIBUTE_UNUSED __attribute__((unused))
#endif
#else
#define ATTRIBUTE_UNUSED
#endif

/**
 * TODO:
 *
 * macro to flag unimplemented blocks
 */
#define TODO 								\
    fprintf(stderr, "Unimplemented block at %s:%d\n",			\
            __FILE__, __LINE__);

/**
 * VIR_CONNECT_MAGIC:
 *
 * magic value used to protect the API when pointers to connection structures
 * are passed down by the uers.
 */
#define VIR_CONNECT_MAGIC 	0x4F23DEAD
#define VIR_IS_CONNECT(obj)	((obj) && (obj)->magic==VIR_CONNECT_MAGIC)


/**
 * VIR_DOMAIN_MAGIC:
 *
 * magic value used to protect the API when pointers to domain structures
 * are passed down by the uers.
 */
#define VIR_DOMAIN_MAGIC		0xDEAD4321
#define VIR_IS_DOMAIN(obj)		((obj) && (obj)->magic==VIR_DOMAIN_MAGIC)
#define VIR_IS_CONNECTED_DOMAIN(obj)	(VIR_IS_DOMAIN(obj) && VIR_IS_CONNECT((obj)->conn))

/*
 * Flags for Xen connections
 */
#define VIR_CONNECT_RO 1

/**
 * _virConnect:
 *
 * Internal structure associated to a connection
 */
struct _virConnect {
    unsigned int magic;		/* specific value to check */
    int	         handle;	/* internal handle used for hypercall */
    struct xs_handle *xshandle;	/* handle to talk to the xenstore */

    /* connection to xend */
    int type;			/* PF_UNIX or PF_INET */
    int len;			/* lenght of addr */
    struct sockaddr *addr;	/* type of address used */
    struct sockaddr_un addr_un;	/* the unix address */
    struct sockaddr_in addr_in; /* the inet address */

    virHashTablePtr   domains;	/* hash table for known domains */
    int          flags;		/* a set of connection flags */
};

/**
 * virDomainFlags:
 *
 * a set of special flag values associated to the domain
 */

enum {
    DOMAIN_IS_SHUTDOWN = (1 << 0)	/* the domain is being shutdown */
} virDomainFlags;

/**
 * _virDomain:
 *
 * Internal structure associated to a domain
 */
struct _virDomain {
    unsigned int magic;		/* specific value to check */
    virConnectPtr conn;		/* pointer back to the connection */
    char        *name;		/* the domain external name */
    char        *path;		/* the domain internal path */
    int	         handle;	/* internal handle for the dmonain ID */
    int          flags;		/* extra flags */
};

/*
 * Internal routines
 */
char *		virDomainGetVM		(virDomainPtr domain);
char *		virDomainGetVMInfo	(virDomainPtr domain,
					 const char *vm,
		          	         const char *name);

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* __VIR_INTERNAL_H__ */
