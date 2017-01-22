# -*- rpm-spec -*-

# This spec file assumes you are building for Fedora 13 or newer,
# or for RHEL 5 or newer. It may need some tweaks for other distros.
# If neither fedora nor rhel was defined, try to guess them from %{dist}
%if !0%{?rhel} && !0%{?fedora}
%{expand:%(echo "%{?dist}" | \
  sed -ne 's/^\.el\([0-9]\+\).*/%%define rhel \1/p')}
%{expand:%(echo "%{?dist}" | \
  sed -ne 's/^\.fc\?\([0-9]\+\).*/%%define fedora \1/p')}
%endif

# Default to skipping autoreconf.  Distros can change just this one line
# (or provide a command-line override) if they backport any patches that
# touch configure.ac or Makefile.am.
# Always run autoreconf
%{!?enable_autotools:%define enable_autotools 1}

# A client only build will create a libvirt.so only containing
# the generic RPC driver, and test driver and no libvirtd
# Default to a full server + client build, but with the possibility
# of a command-line or ~/.rpmmacros override for client-only.
%{!?client_only:%define client_only 0}

# Now turn off server build in certain cases

# RHEL-5 builds are client-only for s390, ppc
%if 0%{?rhel} == 5
    %ifnarch %{ix86} x86_64 ia64
        %define client_only        1
    %endif
%endif

# Disable all server side drivers if client only build requested
%if %{client_only}
    %define server_drivers     0
%else
    %define server_drivers     1
%endif

# Always build with dlopen'd modules
%define with_driver_modules 1

# Now set the defaults for all the important features, independent
# of any particular OS

# First the daemon itself
%define with_libvirtd      0%{!?_without_libvirtd:%{server_drivers}}
%define with_avahi         0%{!?_without_avahi:%{server_drivers}}

# Then the hypervisor drivers that run in libvirtd
%define with_xen           0%{!?_without_xen:%{server_drivers}}
%define with_qemu          0%{!?_without_qemu:%{server_drivers}}
%define with_lxc           0%{!?_without_lxc:%{server_drivers}}
%define with_uml           0%{!?_without_uml:%{server_drivers}}
%define with_libxl         0%{!?_without_libxl:%{server_drivers}}
%define with_vbox          0%{!?_without_vbox:%{server_drivers}}

%define with_qemu_tcg      %{with_qemu}

%define qemu_kvm_arches %{ix86} x86_64

%if 0%{?fedora}
    %if 0%{?fedora} < 16
        # Fedora doesn't have any QEMU on ppc64 until FC16 - only ppc
        # I think F17 is the first release with the power64 macro
        %ifarch ppc64
            %define with_qemu_tcg 0
        %endif
    %endif
    %if 0%{?fedora} >= 18
        %define qemu_kvm_arches %{ix86} x86_64 %{power64} s390x
    %endif
    %if 0%{?fedora} >= 20
        %define qemu_kvm_arches %{ix86} x86_64 %{power64} s390x %{arm} aarch64
    %endif
%endif

%if 0%{?rhel}
    %define with_qemu_tcg 0
    %define qemu_kvm_arches x86_64
    %if 0%{?rhel} >= 7
        %define qemu_kvm_arches x86_64 %{power64} aarch64
    %endif
%endif

%ifarch %{qemu_kvm_arches}
    %define with_qemu_kvm      %{with_qemu}
%else
    %define with_qemu_kvm      0
%endif

%if ! %{with_qemu_tcg} && ! %{with_qemu_kvm}
    %define with_qemu 0
%endif

# Then the hypervisor drivers that run outside libvirtd, in libvirt.so
%define with_openvz        0%{!?_without_openvz:1}
%define with_vmware        0%{!?_without_vmware:1}
%define with_phyp          0%{!?_without_phyp:1}
%define with_esx           0%{!?_without_esx:1}
%define with_hyperv        0%{!?_without_hyperv:1}
%define with_xenapi        0%{!?_without_xenapi:1}
%define with_vz            0%{!?_without_vz:1}
# No test for bhyve, because it does not build on Linux

# Then the secondary host drivers, which run inside libvirtd
%define with_interface        0%{!?_without_interface:%{server_drivers}}
%define with_network          0%{!?_without_network:%{server_drivers}}
%define with_storage_fs       0%{!?_without_storage_fs:%{server_drivers}}
%define with_storage_lvm      0%{!?_without_storage_lvm:%{server_drivers}}
%define with_storage_iscsi    0%{!?_without_storage_iscsi:%{server_drivers}}
%define with_storage_disk     0%{!?_without_storage_disk:%{server_drivers}}
%define with_storage_mpath    0%{!?_without_storage_mpath:%{server_drivers}}
%if 0%{?fedora} >= 16 || 0%{?rhel} >= 7
    %define with_storage_rbd      0%{!?_without_storage_rbd:%{server_drivers}}
%else
    %define with_storage_rbd      0
%endif
%if 0%{?fedora} >= 17
    %define with_storage_sheepdog 0%{!?_without_storage_sheepdog:%{server_drivers}}
%else
    %define with_storage_sheepdog 0
%endif
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 6
    %define with_storage_gluster 0%{!?_without_storage_gluster:%{server_drivers}}
%else
    %define with_storage_gluster 0
%endif
%define with_numactl          0%{!?_without_numactl:%{server_drivers}}
%define with_selinux          0%{!?_without_selinux:%{server_drivers}}

# Just hardcode to off, since few people ever have apparmor RPMs installed
%define with_apparmor         0%{!?_without_apparmor:0}

# A few optional bits off by default, we enable later
%define with_polkit        0%{!?_without_polkit:0}
%define with_capng         0%{!?_without_capng:0}
%define with_fuse          0%{!?_without_fuse:0}
%define with_netcf         0%{!?_without_netcf:0}
%define with_udev          0%{!?_without_udev:0}
%define with_hal           0%{!?_without_hal:0}
%define with_yajl          0%{!?_without_yajl:0}
%define with_nwfilter      0%{!?_without_nwfilter:0}
%define with_libpcap       0%{!?_without_libpcap:0}
%define with_macvtap       0%{!?_without_macvtap:0}
%define with_libnl         0%{!?_without_libnl:0}
%define with_dtrace        0%{!?_without_dtrace:0}
%define with_cgconfig      0%{!?_without_cgconfig:0}
%define with_sanlock       0%{!?_without_sanlock:0}
%define with_systemd       0%{!?_without_systemd:0}
%define with_numad         0%{!?_without_numad:0}
%define with_firewalld     0%{!?_without_firewalld:0}
%define with_libssh2       0%{!?_without_libssh2:0}
%define with_wireshark     0%{!?_without_wireshark:0}
%define with_systemd_daemon 0%{!?_without_systemd_daemon:0}
%define with_pm_utils      1

# Non-server/HV driver defaults which are always enabled
%define with_sasl          0%{!?_without_sasl:1}
%define with_audit         0%{!?_without_audit:1}


# Finally set the OS / architecture specific special cases

# Xen is available only on i386 x86_64 ia64
%ifnarch %{ix86} x86_64 ia64
    %define with_xen 0
    %define with_libxl 0
%endif

# vbox is available only on i386 x86_64
%ifnarch %{ix86} x86_64
    %define with_vbox 0
%endif

# Numactl is not available on s390[x] and ARM
%ifarch s390 s390x %{arm}
    %define with_numactl 0
%endif

# libgfapi is built only on x86_64 on rhel
%ifnarch x86_64
    %if 0%{?rhel} >= 6
        %define with_storage_gluster 0
    %endif
%endif

# librados and librbd are built only on x86_64 on rhel
%ifnarch x86_64
    %if 0%{?rhel} >= 7
        %define with_storage_rbd 0
    %endif
%endif

# RHEL doesn't ship OpenVZ, VBox, UML, PowerHypervisor,
# VMWare, libxenserver (xenapi), libxenlight (Xen 4.1 and newer),
# or HyperV.
%if 0%{?rhel}
    %define with_openvz 0
    %define with_vbox 0
    %define with_uml 0
    %define with_phyp 0
    %define with_vmware 0
    %define with_xenapi 0
    %define with_libxl 0
    %define with_hyperv 0
    %define with_vz 0
%endif

# Fedora 17 / RHEL-7 are first where we use systemd. Although earlier
# Fedora has systemd, libvirt still used sysvinit there.
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7
    %define with_systemd 1
    %define with_systemd_daemon 1
    %define with_pm_utils 0
%endif

# Fedora 18 / RHEL-7 are first where firewalld support is enabled
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7
    %define with_firewalld 1
%endif

# RHEL-5 is too old for LXC
%if 0%{?rhel} == 5
    %define with_lxc 0
%endif

# RHEL-6 stopped including Xen on all archs.
%if 0%{?rhel} >= 6
    %define with_xen 0
%endif

# Fedora doesn't have new enough Xen for libxl until F18
%if 0%{?fedora} && 0%{?fedora} < 18
    %define with_libxl 0
%endif

# fuse is used to provide virtualized /proc for LXC
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7
    %define with_fuse      0%{!?_without_fuse:1}
%endif

# RHEL 5 lacks newer tools
%if 0%{?rhel} == 5
    %define with_hal       0%{!?_without_hal:%{server_drivers}}
%else
    %define with_polkit    0%{!?_without_polkit:1}
    %define with_capng     0%{!?_without_capng:1}
    %define with_netcf     0%{!?_without_netcf:%{server_drivers}}
    %define with_udev      0%{!?_without_udev:%{server_drivers}}
    %define with_yajl      0%{!?_without_yajl:%{server_drivers}}
    %define with_dtrace 1
%endif

# interface requires netcf
%if ! 0%{?with_netcf}
    %define with_interface     0
%endif

# Enable sanlock library for lock management with QEMU
# Sanlock is available only on arches where kvm is available for RHEL
%if 0%{?fedora} >= 16
    %define with_sanlock 0%{!?_without_sanlock:%{server_drivers}}
%endif
%if 0%{?rhel} >= 6
    %ifarch %{qemu_kvm_arches}
        %define with_sanlock 0%{!?_without_sanlock:%{server_drivers}}
    %endif
%endif

# Enable libssh2 transport for new enough distros
%if 0%{?fedora} >= 17
    %define with_libssh2 0%{!?_without_libssh2:1}
%endif

# Enable wireshark plugins for all distros shipping libvirt 1.2.2 or newer
%if 0%{?fedora} >= 21
    %define with_wireshark 0%{!?_without_wireshark:1}
%endif

# Disable some drivers when building without libvirt daemon.
# The logic is the same as in configure.ac
%if ! %{with_libvirtd}
    %define with_interface 0
    %define with_network 0
    %define with_qemu 0
    %define with_lxc 0
    %define with_uml 0
    %define with_hal 0
    %define with_udev 0
    %define with_storage_fs 0
    %define with_storage_lvm 0
    %define with_storage_iscsi 0
    %define with_storage_mpath 0
    %define with_storage_rbd 0
    %define with_storage_sheepdog 0
    %define with_storage_gluster 0
    %define with_storage_disk 0
%endif

%if %{with_qemu} || %{with_lxc} || %{with_uml}
    %define with_nwfilter 0%{!?_without_nwfilter:%{server_drivers}}
# Enable libpcap library
    %define with_libpcap  0%{!?_without_libpcap:%{server_drivers}}
    %define with_macvtap  0%{!?_without_macvtap:%{server_drivers}}

# numad is used to manage the CPU and memory placement dynamically,
# it's not available on s390[x] and ARM.
    %if 0%{?fedora} >= 17 || 0%{?rhel} >= 6
        %ifnarch s390 s390x %{arm}
            %define with_numad    0%{!?_without_numad:%{server_drivers}}
        %endif
    %endif
%endif

%if %{with_macvtap}
    %define with_libnl 1
%endif

# Pull in cgroups config system
%if 0%{?fedora} || 0%{?rhel} >= 6
    %if %{with_qemu} || %{with_lxc}
        %define with_cgconfig 0%{!?_without_cgconfig:1}
    %endif
%endif

%if %{with_udev} || %{with_hal}
    %define with_nodedev 1
%else
    %define with_nodedev 0
%endif

%if %{with_storage_fs} || %{with_storage_mpath} || %{with_storage_iscsi} || %{with_storage_lvm} || %{with_storage_disk}
    %define with_storage 1
%else
    %define with_storage 0
%endif


# Force QEMU to run as non-root
%if 0%{?fedora} || 0%{?rhel} >= 6
    %define qemu_user  qemu
    %define qemu_group  qemu
%else
    %define qemu_user  root
    %define qemu_group  root
%endif


# Advertise OVMF and AAVMF from nightly firmware repo
%if 0%{?fedora}
    %define with_loader_nvram --with-loader-nvram="/usr/share/edk2.git/ovmf-x64/OVMF_CODE-pure-efi.fd:/usr/share/edk2.git/ovmf-x64/OVMF_VARS-pure-efi.fd:/usr/share/edk2.git/aarch64/QEMU_EFI-pflash.raw:/usr/share/edk2.git/aarch64/vars-template-pflash.raw"
%endif


# The RHEL-5 Xen package has some feature backports. This
# flag is set to enable use of those special bits on RHEL-5
%if 0%{?rhel} == 5
    %define with_rhel5  1
%else
    %define with_rhel5  0
%endif

%if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
    %define with_systemd_macros 1
%else
    %define with_systemd_macros 0
%endif


# RHEL releases provide stable tool chains and so it is safe to turn
# compiler warning into errors without being worried about frequent
# changes in reported warnings
%if 0%{?rhel}
    %define enable_werror --enable-werror
%else
    %define enable_werror --disable-werror
%endif


Summary: Library providing a simple virtualization API
Name: libvirt
Version: 1.2.17
Release: 13%{?dist}.5.1%{?extra_release}
License: LGPLv2+
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
URL: http://libvirt.org/

%if %(echo %{version} | grep -o \\. | wc -l) == 3
    %define mainturl stable_updates/
%endif
Source: http://libvirt.org/sources/%{?mainturl}libvirt-%{version}.tar.gz

Patch1: libvirt-RHEL-screenshot-Implement-multiple-screen-support.patch
Patch2: libvirt-RHEL-Support-virtio-disk-hotplug-in-JSON-mode.patch
Patch3: libvirt-RHEL-Add-support-for-QMP-I-O-error-reason.patch
Patch4: libvirt-RHEL-qemu-support-relative-backing-for-RHEL-7.0.z-qemu.patch
Patch5: libvirt-RHEL-Fix-maxvcpus-output.patch
Patch6: libvirt-RHEL-Hack-around-changed-Broadwell-Haswell-CPUs.patch
Patch7: libvirt-util-bitmap-Don-t-alloc-overly-large-binary-bitmaps.patch
Patch8: libvirt-storage-Fix-regression-in-storagePoolUpdateAllState.patch
Patch9: libvirt-Separate-isa-fdc-options-generation.patch
Patch10: libvirt-Explicitly-format-the-isa-fdc-controller-for-newer-q35-machines.patch
Patch11: libvirt-Add-rhel-machine-types-to-qemuDomainMachineNeedsFDC.patch
Patch12: libvirt-conf-Don-t-allow-duplicated-target-names-regardless-of-bus.patch
Patch13: libvirt-storage-Revert-volume-obj-list-updating-after-volume-creation-4749d82a.patch
Patch14: libvirt-qemu_monitor-Wire-up-MIGRATION-event.patch
Patch15: libvirt-qemu-Enable-migration-events-on-QMP-monitor.patch
Patch16: libvirt-qemuDomainGetJobStatsInternal-Support-migration-events.patch
Patch17: libvirt-qemu-Update-migration-state-according-to-MIGRATION-event.patch
Patch18: libvirt-qemu-Wait-for-migration-events-on-domain-condition.patch
Patch19: libvirt-qemu-Check-duplicate-WWNs-also-for-hotplugged-disks.patch
Patch20: libvirt-qemu-move-the-guest-status-check-before-agent-config-and-status-check.patch
Patch21: libvirt-qemu-report-error-for-non-existing-disk-in-blockjobinfo.patch
Patch22: libvirt-virCondWaitUntil-add-another-return-value.patch
Patch23: libvirt-virDomainObjSignal-drop-this-function.patch
Patch24: libvirt-monitor-detect-that-eject-fails-because-the-tray-is-locked.patch
Patch25: libvirt-qemu_hotplug-try-harder-to-eject-media.patch
Patch26: libvirt-qemu-Drop-LFs-at-the-end-of-error-from-QEMU-log.patch
Patch27: libvirt-Introduce-virHashAtomic.patch
Patch28: libvirt-Introduce-virErrorCopyNew.patch
Patch29: libvirt-qemu-Remember-incoming-migration-errors.patch
Patch30: libvirt-qemu-Don-t-report-false-error-from-MigrateFinish.patch
Patch31: libvirt-qemu-Use-error-from-Finish-instead-of-unexpectedly-failed.patch
Patch32: libvirt-cpu-Add-support-for-MPX-and-AVX512-Intel-features.patch
Patch33: libvirt-qemuProcessHandleMigrationStatus-Update-migration-status-more-frequently.patch
Patch34: libvirt-qemuDomainSetNumaParamsLive-Check-for-NUMA-mode-more-wisely.patch
Patch35: libvirt-qemu-process-Improve-update-of-maximum-balloon-state-at-startup.patch
Patch36: libvirt-storage-Fix-pool-building-when-directory-already-exists.patch
Patch37: libvirt-virsh-report-error-if-vcpu-number-exceed-the-guest-maxvcpu-number.patch
Patch38: libvirt-cmdVcpuPin-Remove-dead-code.patch
Patch39: libvirt-rpc-Add-virNetDaemonHasClients.patch
Patch40: libvirt-rpc-Rework-timerActive-logic-in-daemon.patch
Patch41: libvirt-cgroup-Drop-resource-partition-from-virSystemdMakeScopeName.patch
Patch42: libvirt-virsh-blockjob-Extract-block-job-info-code-into-a-separate-function.patch
Patch43: libvirt-virsh-cmdBlockJob-Switch-to-declarative-flag-interlocking.patch
Patch44: libvirt-virsh-blockjob-Split-out-vshBlockJobSetSpeed-from-blockJobImpl.patch
Patch45: libvirt-virsh-block-job-separate-abort-from-blockJobImpl.patch
Patch46: libvirt-virsh-Split-out-block-pull-implementation-from-blockJobImpl.patch
Patch47: libvirt-virsh-Kill-blockJobImpl-by-moving-the-final-impl-into-cmdBlockCommit.patch
Patch48: libvirt-virsh-Refactor-argument-checking-in-cmdBlockCommit.patch
Patch49: libvirt-virsh-Refactor-argument-handling-in-cmdBlockCopy.patch
Patch50: libvirt-virsh-Refactor-argument-handling-in-cmdBlockPull.patch
Patch51: libvirt-qemu-Update-state-of-block-job-to-READY-only-if-it-actually-is-ready.patch
Patch52: libvirt-virsh-Refactor-block-job-waiting-in-cmdBlockPull.patch
Patch53: libvirt-virsh-Refactor-block-job-waiting-in-cmdBlockCommit.patch
Patch54: libvirt-virsh-Refactor-block-job-waiting-in-cmdBlockCopy.patch
Patch55: libvirt-qemu-Reject-migration-with-memory-hotplug-if-destination-doesn-t-support-it.patch
Patch56: libvirt-qemu-Properly-check-for-incoming-migration-job.patch
Patch57: libvirt-qemu-Do-not-reset-labels-when-migration-fails.patch
Patch58: libvirt-qemu-Check-for-iotune_max-support-properly.patch
Patch59: libvirt-docs-Add-Fibre-Channel-NPIV-supported-option-for-volume-lun-config.patch
Patch60: libvirt-conf-Allow-error-reporting-in-virDomainDiskSourceIsBlockType.patch
Patch61: libvirt-qemu-Forbid-image-pre-creation-for-non-shared-storage-migration.patch
Patch62: libvirt-qemu-remove-deadcode-in-qemuDomain-HelperGetVcpus-GetIOThreadsLive.patch
Patch63: libvirt-nodeinfo-Introduce-local-linuxGetCPUPresentPath.patch
Patch64: libvirt-nodeinfo-Add-sysfs_prefix-to-nodeGetCPUCount.patch
Patch65: libvirt-nodeinfo-Add-sysfs_prefix-to-nodeGetPresentCPUBitmap.patch
Patch66: libvirt-nodeinfo-Add-sysfs_prefix-to-nodeGetCPUBitmap.patch
Patch67: libvirt-nodeinfo-Add-sysfs_prefix-to-nodeGetCPUMap.patch
Patch68: libvirt-nodeinfo-Add-sysfs_prefix-to-nodeGetInfo.patch
Patch69: libvirt-nodeinfo-Add-sysfs_prefix-to-nodeCapsInitNUMA.patch
Patch70: libvirt-nodeinfo-Add-sysfs_prefix-to-nodeGetMemoryStats.patch
Patch71: libvirt-nodeinfo-fix-to-parse-present-cpus-rather-than-possible-cpus.patch
Patch72: libvirt-tests-Add-nodeinfo-test-for-non-present-CPUs.patch
Patch73: libvirt-nodeinfo-Make-sysfs_prefix-usage-more-consistent.patch
Patch74: libvirt-nodeinfo-Formatting-changes.patch
Patch75: libvirt-tests-Restore-links-in-deconfigured-cpus-nodeinfo-test.patch
Patch76: libvirt-nodeinfo-Add-nodeGetPresentCPUBitmap-to-libvirt_private.syms.patch
Patch77: libvirt-nodeinfo-Fix-nodeGetCPUBitmap-s-fallback-code-path.patch
Patch78: libvirt-nodeinfo-Introduce-linuxGetCPUGlobalPath.patch
Patch79: libvirt-nodeinfo-Introduce-linuxGetCPUOnlinePath.patch
Patch80: libvirt-nodeinfo-Rename-linuxParseCPUmax-to-linuxParseCPUCount.patch
Patch81: libvirt-nodeinfo-Add-old-kernel-compatibility-to-nodeGetPresentCPUBitmap.patch
Patch82: libvirt-nodeinfo-Remove-out-parameter-from-nodeGetCPUBitmap.patch
Patch83: libvirt-nodeinfo-Rename-nodeGetCPUBitmap-to-nodeGetOnlineCPUBitmap.patch
Patch84: libvirt-nodeinfo-Phase-out-cpu_set_t-usage.patch
Patch85: libvirt-nodeinfo-Use-nodeGetOnlineCPUBitmap-when-parsing-node.patch
Patch86: libvirt-nodeinfo-Use-a-bitmap-to-keep-track-of-node-CPUs.patch
Patch87: libvirt-nodeinfo-Calculate-present-and-online-CPUs-only-once.patch
Patch88: libvirt-nodeinfo-Check-for-errors-when-reading-core_id.patch
Patch89: libvirt-Renamed-deconfigured-cpus-to-allow-make-dist.patch
Patch90: libvirt-tests-Finish-rename-of-the-long-nodeinfo-test-case.patch
Patch91: libvirt-nodeinfo-Fix-output-on-PPC64-KVM-hosts.patch
Patch92: libvirt-tests-Prepare-for-subcore-tests.patch
Patch93: libvirt-tests-Add-subcores1-nodeinfo-test.patch
Patch94: libvirt-tests-Add-subcores2-nodeinfo-test.patch
Patch95: libvirt-tests-Add-subcores3-nodeinfo-test.patch
Patch96: libvirt-nodeinfo-Fix-build-failure-when-KVM-headers-are-not-available.patch
Patch97: libvirt-qemu-fix-some-api-cannot-work-when-disable-cpuset-in-conf.patch
Patch98: libvirt-qemu-Auto-assign-pci-addresses-for-shared-memory-devices.patch
Patch99: libvirt-conf-Add-getter-for-network-routes.patch
Patch100: libvirt-network-Add-another-collision-check-into-networkCheckRouteCollision.patch
Patch101: libvirt-docs-Document-how-libvirt-handles-companion-controllers.patch
Patch102: libvirt-qemu-Reject-updating-unsupported-disk-information.patch
Patch103: libvirt-numa_conf-Introduce-virDomainNumaGetMaxCPUID.patch
Patch104: libvirt-virDomainDefParseXML-Check-for-malicious-cpu-ids-in-numa.patch
Patch105: libvirt-conf-more-useful-error-message-when-pci-function-is-out-of-range.patch
Patch106: libvirt-qemu-Fix-reporting-of-physical-capacity-for-block-devices.patch
Patch107: libvirt-network-verify-proper-address-family-in-updates-to-host-and-range.patch
Patch108: libvirt-rpc-Remove-keepalive_required-option.patch
Patch109: libvirt-virNetDevBandwidthParseRate-Reject-negative-values.patch
Patch110: libvirt-domain-Fix-crash-if-trying-to-live-update-disk-serial.patch
Patch111: libvirt-qemu-fail-on-attempts-to-use-filterref-for-non-tap-network-connections.patch
Patch112: libvirt-network-validate-network-NAT-range.patch
Patch113: libvirt-conf-Don-t-try-formating-non-existing-addresses.patch
Patch114: libvirt-cpu-Rename-powerpc-ppc-ppc64-filesystem.patch
Patch115: libvirt-cpu-Rename-powerpc-ppc-ppc64-exported-symbols.patch
Patch116: libvirt-cpu-Rename-powerpc-ppc-ppc64-internal-symbols.patch
Patch117: libvirt-cpu-Indentation-changes-in-the-ppc64-driver.patch
Patch118: libvirt-cpu-Mark-driver-functions-in-ppc64-driver.patch
Patch119: libvirt-cpu-Simplify-NULL-handling-in-ppc64-driver.patch
Patch120: libvirt-cpu-Simplify-ppc64ModelFromCPU.patch
Patch121: libvirt-cpu-Reorder-functions-in-the-ppc64-driver.patch
Patch122: libvirt-cpu-Remove-ISA-information-from-CPU-map-XML.patch
Patch123: libvirt-tests-Remove-unused-file.patch
Patch124: libvirt-tests-Improve-result-handling-in-cpuTestGuestData.patch
Patch125: libvirt-cpu-Never-skip-CPU-model-name-check-in-ppc64-driver.patch
Patch126: libvirt-cpu-CPU-model-names-have-to-match-on-ppc64.patch
Patch127: libvirt-cpu-Use-ppc64Compute-to-implement-ppc64DriverCompare.patch
Patch128: libvirt-tests-Temporarily-disable-ppc64-cpu-tests.patch
Patch129: libvirt-cpu-Align-ppc64-CPU-data-with-x86.patch
Patch130: libvirt-cpu-Support-multiple-PVRs-in-the-ppc64-driver.patch
Patch131: libvirt-cpu-Simplify-ppc64-part-of-CPU-map-XML.patch
Patch132: libvirt-cpu-Parse-and-use-PVR-masks-in-the-ppc64-driver.patch
Patch133: libvirt-cpu-Add-POWER8NVL-information-to-CPU-map-XML.patch
Patch134: libvirt-cpu-Implement-backwards-compatibility-in-the-ppc64-driver.patch
Patch135: libvirt-cpu-Forbid-model-fallback-in-the-ppc64-driver.patch
Patch136: libvirt-tests-Re-enable-ppc64-cpu-tests.patch
Patch137: libvirt-tests-Add-a-bunch-of-cpu-test-case-for-ppc64.patch
Patch138: libvirt-cpu-Fix-segfault-in-the-ppc64-driver.patch
Patch139: libvirt-qemu-Fix-segfault-when-parsing-private-domain-data.patch
Patch140: libvirt-conf-Pass-private-data-to-Parse-function-of-XML-options.patch
Patch141: libvirt-qemu-Keep-numad-hint-after-daemon-restart.patch
Patch142: libvirt-qemu-Use-numad-information-when-getting-pin-information.patch
Patch143: libvirt-api-Remove-check-on-iothread_id-arg-in-virDomainPinIOThread.patch
Patch144: libvirt-api-Adjust-comment-for-virDomainAddIOThread.patch
Patch145: libvirt-qemu-Add-check-for-invalid-iothread_id-in-qemuDomainChgIOThread.patch
Patch146: libvirt-conf-Check-for-attach-disk-usage-of-iothread-0.patch
Patch147: libvirt-virNetDevBandwidthUpdateRate-turn-class_id-into-integer.patch
Patch148: libvirt-bridge_driver-Introduce-networkBandwidthChangeAllowed.patch
Patch149: libvirt-bridge_driver-Introduce-networkBandwidthUpdate.patch
Patch150: libvirt-qemuDomainSetInterfaceParameters-Use-new-functions-to-update-bandwidth.patch
Patch151: libvirt-cpu-Don-t-update-host-model-guest-CPUs-on-ppc64.patch
Patch152: libvirt-cpu-Better-support-for-ppc64-compatibility-modes.patch
Patch153: libvirt-cpu-Move-check-for-NULL-CPU-model-inside-the-driver.patch
Patch154: libvirt-tests-Add-some-compatibility-related-cases-to-the-CPU-tests.patch
Patch155: libvirt-Start-daemon-only-after-filesystems-are-mounted.patch
Patch156: libvirt-virfile-Add-error-for-root-squash-change-mode-failure.patch
Patch157: libvirt-virfile-Introduce-virFileUnlink.patch
Patch158: libvirt-storage-Correct-the-mode-check.patch
Patch159: libvirt-storage-Handle-failure-from-refreshVol.patch
Patch160: libvirt-util-Add-virStringGetFirstWithPrefix.patch
Patch161: libvirt-util-Add-virCgroupGetBlockDevString.patch
Patch162: libvirt-util-Add-getters-for-cgroup-block-device-I-O-throttling.patch
Patch163: libvirt-lxc-Sync-BlkioDevice-values-when-setting-them-in-cgroups.patch
Patch164: libvirt-qemu-Sync-BlkioDevice-values-when-setting-them-in-cgroups.patch
Patch165: libvirt-Allow-vfio-hotplug-of-a-device-to-the-domain-which-owns-the-iommu.patch
Patch166: libvirt-hostdev-skip-ACS-check-when-using-VFIO-for-device-assignment.patch
Patch167: libvirt-docs-Clarify-unprivileged-sgio-feature.patch
Patch168: libvirt-qemu-Introduce-qemuIsSharedHostdev.patch
Patch169: libvirt-qemu-Introduce-qemuGetHostdevPath.patch
Patch170: libvirt-qemu-Refactor-qemuCheckSharedDisk-to-create-qemuCheckUnprivSGIO.patch
Patch171: libvirt-qemu-Inline-qemuGetHostdevPath.patch
Patch172: libvirt-qemu-Refactor-qemuSetUnprivSGIO-return-values.patch
Patch173: libvirt-qemu-Fix-integer-boolean-logic-in-qemuSetUnprivSGIO.patch
Patch174: libvirt-RHEL-qemu-Add-ability-to-set-sgio-values-for-hostdev.patch
Patch175: libvirt-RHEL-qemu-Add-check-for-unpriv-sgio-for-SCSI-generic-host-device.patch
Patch176: libvirt-security_selinux-Use-proper-structure-to-access-socket-data.patch
Patch177: libvirt-security_dac-Label-non-listening-sockets.patch
Patch178: libvirt-security-Add-virSecurityDomainSetDirLabel.patch
Patch179: libvirt-security_stack-Add-SetDirLabel-support.patch
Patch180: libvirt-security_selinux-Add-SetDirLabel-support.patch
Patch181: libvirt-security_dac-Add-SetDirLabel-support.patch
Patch182: libvirt-qemu-Fix-access-to-auto-generated-socket-paths.patch
Patch183: libvirt-tests-Use-qemuProcessPrepareMonitorChr-in-qemuxmlnstest.patch
Patch184: libvirt-qemu-Label-correct-per-VM-path-when-starting.patch
Patch185: libvirt-selinux-fix-compile-errors.patch
Patch186: libvirt-conf-Add-ioeventfd-option-for-controllers.patch
Patch187: libvirt-qemu-Enable-ioeventfd-usage-for-virtio-scsi-controllers.patch
Patch188: libvirt-util-make-virNetDev-Replace-Restore-MacAddress-public-functions.patch
Patch189: libvirt-util-don-t-use-netlink-to-save-set-mac-for-macvtap-passthrough-802.1Qbh.patch
Patch190: libvirt-cpu-Introduce-IvyBridge-CPU-model.patch
Patch191: libvirt-examples-Add-example-polkit-ACL-rules.patch
Patch192: libvirt-qemu-don-t-use-initialized-ret-in-qemuRemoveSharedDevice.patch
Patch193: libvirt-qemu-Introduce-qemuDomainMachineIsS390CCW.patch
Patch194: libvirt-qemu-Need-to-check-for-machine.os-when-using-ADDRESS_TYPE_CCW.patch
Patch195: libvirt-conf-fix-crash-when-parsing-a-unordered-NUMA-cell.patch
Patch196: libvirt-vmx-Some-whitespace-cleanup.patch
Patch197: libvirt-vmx-The-virVMXParseDisk-deviceType-can-be-NULL-add-some-missing-checks.patch
Patch198: libvirt-vmx-Add-handling-for-CDROM-devices-with-SCSI-passthru.patch
Patch199: libvirt-qemu-hotplug-Properly-clean-up-drive-backend-if-frontend-hotplug-fails.patch
Patch200: libvirt-qemu-Introduce-QEMU_CAPS_DEVICE_RTL8139.patch
Patch201: libvirt-qemu-Introduce-QEMU_CAPS_DEVICE_E1000.patch
Patch202: libvirt-qemu-Introduce-QEMU_CAPS_DEVICE_VIRTIO_NET.patch
Patch203: libvirt-qemu-Try-several-network-devices-when-looking-for-a-default.patch
Patch204: libvirt-qemu-Report-error-if-per-VM-directory-cannot-be-created.patch
Patch205: libvirt-qemu-Do-not-allow-others-into-per-VM-subdirectories.patch
Patch206: libvirt-qemu-Allow-others-to-browse-var-lib-libvirt-qemu.patch
Patch207: libvirt-virSecuritySELinuxSetSecurityAllLabel-drop-useless-virFileIsSharedFSType.patch
Patch208: libvirt-security_selinux-Replace-SELinuxSCSICallbackData-with-proper-struct.patch
Patch209: libvirt-virSecurityManager-Track-if-running-as-privileged.patch
Patch210: libvirt-security_selinux-Take-privileged-into-account.patch
Patch211: libvirt-qemu-Fix-using-guest-architecture-as-lookup-key.patch
Patch212: libvirt-virfile-Check-for-existence-of-dir-in-virFileDeleteTree.patch
Patch213: libvirt-Revert-qemu-Fix-integer-boolean-logic-in-qemuSetUnprivSGIO.patch
Patch214: libvirt-qemu-migration-Relax-enforcement-of-memory-hotplug-support.patch
Patch215: libvirt-conf-Add-helper-to-determine-whether-memory-hotplug-is-enabled-for-a-vm.patch
Patch216: libvirt-qemu-Make-memory-alignment-helper-more-universal.patch
Patch217: libvirt-conf-Drop-VIR_DOMAIN_DEF_PARSE_CLOCK_ADJUST-flag.patch
Patch218: libvirt-conf-Document-all-VIR_DOMAIN_DEF_PARSE_-flags.patch
Patch219: libvirt-conf-Add-XML-parser-flag-that-will-allow-us-to-do-incompatible-updates.patch
Patch220: libvirt-conf-Split-memory-related-post-parse-stuff-into-separate-function.patch
Patch221: libvirt-conf-Rename-max_balloon-to-total_memory.patch
Patch222: libvirt-conf-Pre-calculate-initial-memory-size-instead-of-always-calculating-it.patch
Patch223: libvirt-conf-Don-t-always-recalculate-initial-memory-size-from-NUMA-size-totals.patch
Patch224: libvirt-qemu-command-Align-memory-sizes-only-on-fresh-starts.patch
Patch225: libvirt-qemu-ppc64-Align-memory-sizes-to-256MiB-blocks.patch
Patch226: libvirt-test-Add-test-to-validate-that-memory-sizes-don-t-get-updated-on-migration.patch
Patch227: libvirt-qemu-Align-memory-module-sizes-to-2MiB.patch
Patch228: libvirt-qemu-Refresh-memory-size-only-on-fresh-starts.patch
Patch229: libvirt-domain-Fix-migratable-XML-with-graphics-listen.patch
Patch230: libvirt-qemu-Fix-dynamic_ownership-qemu.conf-setting.patch
Patch231: libvirt-qemu-Add-conditions-for-qemu-kvm-use-on-ppc64.patch
Patch232: libvirt-qemu-Move-simplification-variable-to-begining-of-the-function.patch
Patch233: libvirt-qemu-Extract-mem-path-building-into-its-own-function.patch
Patch234: libvirt-qemu-Add-mem-path-even-with-numa.patch
Patch235: libvirt-qemu-Use-memory-backing-file-only-when-needed.patch
Patch236: libvirt-qemu-Always-update-migration-times-on-destination.patch
Patch237: libvirt-qemu-Copy-completed-migration-stats-only-on-success.patch
Patch238: libvirt-qemu-Introduce-flags-in-qemuMigrationCompleted.patch
Patch239: libvirt-qemu-Make-updating-stats-in-qemuMigrationCheckJobStatus-optional.patch
Patch240: libvirt-qemu-Wait-until-destination-QEMU-consumes-all-migration-data.patch
Patch241: libvirt-qemu-migration-Properly-parse-memory-hotplug-migration-flag.patch
Patch242: libvirt-qemu-Emit-correct-audit-message-for-memory-hot-unplug.patch
Patch243: libvirt-qemu-Emit-correct-audit-message-for-memory-hot-plug.patch
Patch244: libvirt-qemu-Extract-logic-to-determine-the-mlock-limit-size-for-VFIO.patch
Patch245: libvirt-qemu-hotplug-Fix-mlock-limit-handling-on-memory-hotplug.patch
Patch246: libvirt-qemu-domain-Restructurate-control-flow-in-qemuDomainGetMlockLimitBytes.patch
Patch247: libvirt-qemu-Explain-mlock-limit-size-more-in-detail.patch
Patch248: libvirt-qemu-hotplug-Reject-VFIO-hotplug-if-setting-RLIMIT_MEMLOCK-fails.patch
Patch249: libvirt-process-Log-when-limiting-the-amount-of-locked-memory.patch
Patch250: libvirt-qemu-Use-qemuDomainRequiresMlock-in-qemuBuildCommandLine.patch
Patch251: libvirt-qemu-Use-qemuDomainRequiresMlock-when-attaching-PCI-hostdev.patch
Patch252: libvirt-qemu-Add-ppc64-specific-math-to-qemuDomainGetMlockLimitBytes.patch
Patch253: libvirt-qemu-Always-set-locked-memory-limit-for-ppc64-domains.patch
Patch254: libvirt-qemu-Support-vhost-user-multiqueue-with-QEMU-2.3.patch
Patch255: libvirt-vmx-Adapt-to-emptyBackingString-for-cdrom-image.patch
Patch256: libvirt-systemd-Escape-machine-name-for-machined.patch
Patch257: libvirt-systemd-Add-virSystemdGetMachineNameByPID.patch
Patch258: libvirt-systemd-Modernize-machine-naming.patch
Patch259: libvirt-virSystemdGetMachineNameByPID-Initialize-reply.patch
Patch260: libvirt-util-Fix-virCgroupNewMachine-ATTRIBUTE_NONNULL-args.patch
Patch261: libvirt-dbus-Don-t-unref-NULL-messages.patch
Patch262: libvirt-vmx-Expose-datacenter-path-in-domain-XML.patch
Patch263: libvirt-nodedev-Indent-PCI-express-for-future-fix.patch
Patch264: libvirt-nodedev-Expose-PCI-header-type.patch
Patch265: libvirt-nodedev-Fix-parsing-of-generated-XMLs.patch
Patch266: libvirt-qemu-driver-Remove-unnecessary-flag-in-qemuDomainGetStatsBlock.patch
Patch267: libvirt-qemu-driver-Separate-bulk-stats-worker-for-block-devices.patch
Patch268: libvirt-qemu-bulk-stats-Don-t-access-possibly-blocked-storage.patch

Patch10000: libvirt-qemu-agent-Fix-QEMU-guest-agent-is-not-available-due-to-an-error.patch

%if %{with_libvirtd}
Requires: libvirt-daemon = %{version}-%{release}
    %if %{with_network}
Requires: libvirt-daemon-config-network = %{version}-%{release}
    %endif
    %if %{with_nwfilter}
Requires: libvirt-daemon-config-nwfilter = %{version}-%{release}
    %endif
    %if %{with_driver_modules}
        %if %{with_libxl}
Requires: libvirt-daemon-driver-libxl = %{version}-%{release}
        %endif
        %if %{with_lxc}
Requires: libvirt-daemon-driver-lxc = %{version}-%{release}
        %endif
        %if %{with_qemu}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
        %endif
        %if %{with_uml}
Requires: libvirt-daemon-driver-uml = %{version}-%{release}
        %endif
        %if %{with_xen}
Requires: libvirt-daemon-driver-xen = %{version}-%{release}
        %endif
        %if %{with_vbox}
Requires: libvirt-daemon-driver-vbox = %{version}-%{release}
        %endif
        %if %{with_nwfilter}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
        %endif

	%if %{with_interface}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
	%endif
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
    %endif
%endif
Requires: libvirt-client = %{version}-%{release}

# All build-time requirements. Run-time requirements are
# listed against each sub-RPM
%if 0%{?enable_autotools}
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: gettext-devel
BuildRequires: libtool
BuildRequires: /usr/bin/pod2man
%endif
BuildRequires: git
BuildRequires: perl
BuildRequires: perl-XML-XPath
BuildRequires: python
%if %{with_systemd}
BuildRequires: systemd-units
%endif
%if %{with_systemd_daemon}
BuildRequires: systemd-devel
%endif
%if %{with_xen} || %{with_libxl}
BuildRequires: xen-devel
%endif
BuildRequires: libxml2-devel
BuildRequires: xhtml1-dtds
BuildRequires: libxslt
BuildRequires: readline-devel
BuildRequires: ncurses-devel
BuildRequires: gettext
BuildRequires: libtasn1-devel
%if (0%{?rhel} && 0%{?rhel} < 7) || (0%{?fedora} && 0%{?fedora} < 19)
BuildRequires: libgcrypt-devel
%endif
BuildRequires: gnutls-devel
BuildRequires: libattr-devel
%if %{with_libvirtd}
# For pool-build probing for existing pools
BuildRequires: libblkid-devel >= 2.17
%endif
%if 0%{?fedora} || 0%{?rhel} >= 6
# for augparse, optionally used in testing
BuildRequires: augeas
%endif
%if %{with_hal}
BuildRequires: hal-devel
%endif
%if %{with_udev}
    %if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
BuildRequires: systemd-devel >= 185
    %else
BuildRequires: libudev-devel >= 145
    %endif
BuildRequires: libpciaccess-devel >= 0.10.9
%endif
%if %{with_yajl}
BuildRequires: yajl-devel
%endif
%if %{with_sanlock}
# make sure libvirt is built with new enough sanlock on
# distros that have it; required for on_lockfailure
    %if 0%{?fedora} >= 17 || 0%{?rhel} >= 6
BuildRequires: sanlock-devel >= 2.4
    %else
BuildRequires: sanlock-devel >= 1.8
    %endif
%endif
%if %{with_libpcap}
BuildRequires: libpcap-devel
%endif
%if %{with_libnl}
    %if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
BuildRequires: libnl3-devel
    %else
BuildRequires: libnl-devel
    %endif
%endif
%if %{with_avahi}
BuildRequires: avahi-devel
%endif
%if %{with_selinux}
BuildRequires: libselinux-devel
%endif
%if %{with_apparmor}
BuildRequires: libapparmor-devel
%endif
%if %{with_network}
BuildRequires: dnsmasq >= 2.41
BuildRequires: iptables
    %if (0%{?fedora} && 0%{?fedora} < 17) || (0%{?rhel} && 0%{?rhel} < 7)
BuildRequires: iptables-ipv6
    %endif
BuildRequires: radvd
%endif
%if %{with_nwfilter}
BuildRequires: ebtables
%endif
BuildRequires: module-init-tools
%if %{with_sasl}
BuildRequires: cyrus-sasl-devel
%endif
%if %{with_polkit}
    %if 0%{?fedora} >= 20 || 0%{?rhel} >= 7
BuildRequires: polkit-devel >= 0.112
    %else
        %if 0%{?fedora} || 0%{?rhel} >= 6
BuildRequires: polkit-devel >= 0.93
        %else
BuildRequires: PolicyKit-devel >= 0.6
        %endif
    %endif
%endif
%if %{with_storage_fs}
# For mount/umount in FS driver
BuildRequires: util-linux
%endif
%if %{with_qemu}
# From QEMU RPMs
BuildRequires: /usr/bin/qemu-img
%else
    %if %{with_xen}
# From Xen RPMs
BuildRequires: /usr/sbin/qcow-create
    %endif
%endif
%if %{with_storage_lvm}
# For LVM drivers
BuildRequires: lvm2
%endif
%if %{with_storage_iscsi}
# For ISCSI driver
BuildRequires: iscsi-initiator-utils
%endif
%if %{with_storage_disk}
# For disk driver
BuildRequires: parted-devel
    %if 0%{?rhel} == 5
# Broken RHEL-5 parted RPM is missing a dep
BuildRequires: e2fsprogs-devel
    %endif
%endif
%if %{with_storage_mpath} || %{with_storage_disk}
# For Multipath support
    %if 0%{?rhel} == 5
# Broken RHEL-5 packaging has header files in main RPM :-(
BuildRequires: device-mapper
    %else
BuildRequires: device-mapper-devel
    %endif
%endif
%if %{with_storage_rbd}
    %if 0%{?rhel} >= 7
BuildRequires: librados2-devel
BuildRequires: librbd1-devel
    %else
BuildRequires: ceph-devel
    %endif
%endif
%if %{with_storage_gluster}
    %if 0%{?rhel} >= 6
BuildRequires: glusterfs-api-devel >= 3.4.0
BuildRequires: glusterfs-devel >= 3.4.0
    %else
BuildRequires: glusterfs-api-devel >= 3.4.1
BuildRequires: glusterfs-devel >= 3.4.1
    %endif
%endif
%if %{with_numactl}
# For QEMU/LXC numa info
BuildRequires: numactl-devel
%endif
%if %{with_capng}
BuildRequires: libcap-ng-devel >= 0.5.0
%endif
%if %{with_fuse}
BuildRequires: fuse-devel >= 2.8.6
%endif
%if %{with_phyp} || %{with_libssh2}
BuildRequires: libssh2-devel >= 1.3.0
%endif

%if %{with_netcf}
    %if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
BuildRequires: netcf-devel >= 0.2.2
    %else
        %if 0%{?fedora} >= 16 || 0%{?rhel} >= 6
BuildRequires: netcf-devel >= 0.1.8
        %else
BuildRequires: netcf-devel >= 0.1.4
        %endif
    %endif
%endif
%if %{with_esx}
    %if 0%{?fedora} || 0%{?rhel} >= 6
BuildRequires: libcurl-devel
    %else
BuildRequires: curl-devel
    %endif
%endif
%if %{with_hyperv}
BuildRequires: libwsman-devel >= 2.2.3
%endif
%if %{with_audit}
BuildRequires: audit-libs-devel
%endif
%if %{with_dtrace}
# we need /usr/sbin/dtrace
BuildRequires: systemtap-sdt-devel
%endif

%if %{with_storage_fs}
# For mount/umount in FS driver
BuildRequires: util-linux
# For showmount in FS driver (netfs discovery)
BuildRequires: nfs-utils
%endif

%if %{with_firewalld}
# Communication with the firewall daemon uses DBus
BuildRequires: dbus-devel
%endif

# Fedora build root suckage
BuildRequires: gawk

# For storage wiping with different algorithms
BuildRequires: scrub

%if %{with_numad}
BuildRequires: numad
%endif

%if %{with_wireshark}
BuildRequires: wireshark-devel
%endif

Provides: bundled(gnulib)

%description
Libvirt is a C toolkit to interact with the virtualization capabilities
of recent versions of Linux (and other OSes). The main package includes
the libvirtd server exporting the virtualization support.

%package docs
Summary: API reference and website documentation
Group: Development/Libraries

%description docs
Includes the API reference for the libvirt C library, and a complete
copy of the libvirt.org website documentation.

%if %{with_libvirtd}
%package daemon
Summary: Server side daemon and supporting files for libvirt library
Group: Development/Libraries

# All runtime requirements for the libvirt package (runtime requrements
# for subpackages are listed later in those subpackages)

# The client side, i.e. shared libs and virsh are in a subpackage
Requires: %{name}-client = %{version}-%{release}

# for modprobe of pci devices
Requires: module-init-tools
# for /sbin/ip & /sbin/tc
Requires: iproute
    %if %{with_avahi}
        %if 0%{?rhel} == 5
Requires: avahi
        %else
Requires: avahi-libs
        %endif
    %endif
    %if %{with_polkit}
        %if 0%{?fedora} >= 20 || 0%{?rhel} >= 7
Requires: polkit >= 0.112
        %else
            %if 0%{?fedora} || 0%{?rhel} >=6
Requires: polkit >= 0.93
            %else
Requires: PolicyKit >= 0.6
            %endif
        %endif
    %endif
    %if %{with_cgconfig}
Requires: libcgroup
    %endif
    %ifarch %{ix86} x86_64 ia64
# For virConnectGetSysinfo
Requires: dmidecode
    %endif
# For service management
    %if %{with_systemd}
Requires(post): systemd-units
Requires(post): systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units
    %endif
    %if %{with_numad}
Requires: numad
    %endif
# libvirtd depends on 'messagebus' service
Requires: dbus
# For uid creation during pre
Requires(pre): shadow-utils

%description daemon
Server side daemon required to manage the virtualization capabilities
of recent versions of Linux. Requires a hypervisor specific sub-RPM
for specific drivers.

    %if %{with_network}
%package daemon-config-network
Summary: Default configuration files for the libvirtd daemon
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
        %if %{with_driver_modules}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
        %endif

%description daemon-config-network
Default configuration files for setting up NAT based networking
    %endif

    %if %{with_nwfilter}
%package daemon-config-nwfilter
Summary: Network filter configuration files for the libvirtd daemon
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
        %if %{with_driver_modules}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
        %endif

%description daemon-config-nwfilter
Network filter configuration files for cleaning guest traffic
    %endif

    %if %{with_driver_modules}
        %if %{with_network}
%package daemon-driver-network
Summary: Network driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
Requires: dnsmasq >= 2.41
Requires: radvd
Requires: iptables
            %if (0%{?fedora} && 0%{?fedora} < 17) || (0%{?rhel} && 0%{?rhel} < 7)
Requires: iptables-ipv6
            %endif

%description daemon-driver-network
The network driver plugin for the libvirtd daemon, providing
an implementation of the virtual network APIs using the Linux
bridge capabilities.
        %endif


        %if %{with_nwfilter}
%package daemon-driver-nwfilter
Summary: Nwfilter driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
Requires: iptables
            %if (0%{?fedora} && 0%{?fedora} < 17) || (0%{?rhel} && 0%{?rhel} < 7)
Requires: iptables-ipv6
            %endif
Requires: ebtables

%description daemon-driver-nwfilter
The nwfilter driver plugin for the libvirtd daemon, providing
an implementation of the firewall APIs using the ebtables,
iptables and ip6tables capabilities
        %endif


        %if %{with_nodedev}
%package daemon-driver-nodedev
Summary: Nodedev driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
# needed for device enumeration
            %if %{with_hal}
Requires: hal
            %endif
            %if %{with_udev}
                %if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
Requires: systemd >= 185
                %else
Requires: udev >= 145
                %endif
            %endif

%description daemon-driver-nodedev
The nodedev driver plugin for the libvirtd daemon, providing
an implementation of the node device APIs using the udev
capabilities.
        %endif


        %if %{with_interface}
%package daemon-driver-interface
Summary: Interface driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
            %if %{with_netcf} && (0%{?fedora} >= 18 || 0%{?rhel} >= 7)
Requires: netcf-libs >= 0.2.2
            %endif

%description daemon-driver-interface
The interface driver plugin for the libvirtd daemon, providing
an implementation of the network interface APIs using the
netcf library
        %endif


%package daemon-driver-secret
Summary: Secret driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-secret
The secret driver plugin for the libvirtd daemon, providing
an implementation of the secret key APIs.


        %if %{with_storage}
%package daemon-driver-storage
Summary: Storage driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
            %if %{with_storage_fs}
Requires: nfs-utils
# For mkfs
Requires: util-linux
# For glusterfs
                %if 0%{?fedora}
Requires: glusterfs-client >= 2.0.1
                %endif
            %endif
            %if %{with_storage_lvm}
# For LVM drivers
Requires: lvm2
            %endif
            %if %{with_storage_iscsi}
# For ISCSI driver
Requires: iscsi-initiator-utils
            %endif
            %if %{with_storage_disk}
# For disk driver
Requires: parted
Requires: device-mapper
            %endif
            %if %{with_storage_mpath}
# For multipath support
Requires: device-mapper
            %endif
            %if %{with_storage_sheepdog}
# For Sheepdog support
Requires: sheepdog
            %endif
            %if %{with_qemu}
# From QEMU RPMs
Requires: /usr/bin/qemu-img
            %else
                %if %{with_xen}
# From Xen RPMs
Requires: /usr/sbin/qcow-create
                %endif
            %endif

%description daemon-driver-storage
The storage driver plugin for the libvirtd daemon, providing
an implementation of the storage APIs using LVM, iSCSI,
parted and more.
        %endif


        %if %{with_qemu}
%package daemon-driver-qemu
Summary: Qemu driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
# There really is a hard cross-driver dependency here
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: /usr/bin/qemu-img
# For image compression
Requires: gzip
Requires: bzip2
Requires: lzop
Requires: xz

%description daemon-driver-qemu
The qemu driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
QEMU
        %endif


        %if %{with_lxc}
%package daemon-driver-lxc
Summary: LXC driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}
# There really is a hard cross-driver dependency here
Requires: libvirt-daemon-driver-network = %{version}-%{release}

%description daemon-driver-lxc
The LXC driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
the Linux kernel
        %endif


        %if %{with_uml}
%package daemon-driver-uml
Summary: Uml driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-uml
The UML driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
User Mode Linux
        %endif


        %if %{with_xen}
%package daemon-driver-xen
Summary: Xen driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-xen
The Xen driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
Xen
        %endif


        %if %{with_vbox}
%package daemon-driver-vbox
Summary: VirtualBox driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-vbox
The vbox driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
VirtualBox
        %endif


        %if %{with_libxl}
%package daemon-driver-libxl
Summary: Libxl driver plugin for the libvirtd daemon
Group: Development/Libraries
Requires: libvirt-daemon = %{version}-%{release}

%description daemon-driver-libxl
The Libxl driver plugin for the libvirtd daemon, providing
an implementation of the hypervisor driver APIs using
Libxl
        %endif
    %endif # %{with_driver_modules}



    %if %{with_qemu_tcg}
%package daemon-qemu
Summary: Server side daemon & driver required to run QEMU guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
        %if %{with_driver_modules}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
        %endif
Requires: qemu

%description daemon-qemu
Server side daemon and driver required to manage the virtualization
capabilities of the QEMU TCG emulators
    %endif


    %if %{with_qemu_kvm}
%package daemon-kvm
Summary: Server side daemon & driver required to run KVM guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
        %if %{with_driver_modules}
Requires: libvirt-daemon-driver-qemu = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
        %endif
        %ifnarch %{power64} aarch64
# On ppc64, ppc64le, and aarch64 there is no qemu-kvm, but we need
# libvirt-daemon-kvm to be part of RHEL because layered products depend
# on it.  Luckily, they also directly require qemu-kvm-rhev so it is
# safe (although ugly and dirty) to drop the dependency here.
Requires: qemu-kvm
        %endif

%description daemon-kvm
Server side daemon and driver required to manage the virtualization
capabilities of the KVM hypervisor
    %endif


    %if %{with_lxc}
%package daemon-lxc
Summary: Server side daemon & driver required to run LXC guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
        %if %{with_driver_modules}
Requires: libvirt-daemon-driver-lxc = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
        %endif

%description daemon-lxc
Server side daemon and driver required to manage the virtualization
capabilities of LXC
    %endif


    %if %{with_uml}
%package daemon-uml
Summary: Server side daemon & driver required to run UML guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
        %if %{with_driver_modules}
Requires: libvirt-daemon-driver-uml = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
        %endif
# There are no UML kernel RPMs in Fedora/RHEL to depend on.

%description daemon-uml
Server side daemon and driver required to manage the virtualization
capabilities of UML
    %endif


    %if %{with_xen} || %{with_libxl}
%package daemon-xen
Summary: Server side daemon & driver required to run XEN guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
        %if %{with_driver_modules}
            %if %{with_xen}
Requires: libvirt-daemon-driver-xen = %{version}-%{release}
            %endif
            %if %{with_libxl}
Requires: libvirt-daemon-driver-libxl = %{version}-%{release}
            %endif
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
        %endif
Requires: xen

%description daemon-xen
Server side daemon and driver required to manage the virtualization
capabilities of XEN
    %endif

    %if %{with_vbox}
%package daemon-vbox
Summary: Server side daemon & driver required to run VirtualBox guests
Group: Development/Libraries

Requires: libvirt-daemon = %{version}-%{release}
        %if %{with_driver_modules}
Requires: libvirt-daemon-driver-vbox = %{version}-%{release}
Requires: libvirt-daemon-driver-interface = %{version}-%{release}
Requires: libvirt-daemon-driver-network = %{version}-%{release}
Requires: libvirt-daemon-driver-nodedev = %{version}-%{release}
Requires: libvirt-daemon-driver-nwfilter = %{version}-%{release}
Requires: libvirt-daemon-driver-secret = %{version}-%{release}
Requires: libvirt-daemon-driver-storage = %{version}-%{release}
        %endif

%description daemon-vbox
Server side daemon and driver required to manage the virtualization
capabilities of VirtualBox
    %endif
%endif # %{with_libvirtd}

%package client
Summary: Client side library and utilities of the libvirt library
Group: Development/Libraries
Requires: readline
Requires: ncurses
# So remote clients can access libvirt over SSH tunnel
# (client invokes 'nc' against the UNIX socket on the server)
Requires: nc
# Needed by /usr/libexec/libvirt-guests.sh script.
Requires: gettext
# Needed by virt-pki-validate script.
Requires: gnutls-utils
%if %{with_pm_utils}
# Needed for probing the power management features of the host.
Requires: pm-utils
%endif
%if %{with_sasl}
Requires: cyrus-sasl
# Not technically required, but makes 'out-of-box' config
# work correctly & doesn't have onerous dependencies
Requires: cyrus-sasl-md5
%endif

%description client
Shared libraries and client binaries needed to access to the
virtualization capabilities of recent versions of Linux (and other OSes).

%if %{with_wireshark}
%package wireshark
Summary: Wireshark dissector plugin for libvirt RPC transactions
Group: Development/Libraries
Requires: wireshark
Requires: %{name}-client = %{version}-%{release}

%description wireshark
Wireshark dissector plugin for better analysis of libvirt RPC traffic.
%endif

%if %{with_lxc}
%package login-shell
Summary: Login shell for connecting users to an LXC container
Group: Development/Libraries
Requires: %{name}-client = %{version}-%{release}

%description login-shell
Provides the set-uid virt-login-shell binary that is used to
connect a user to an LXC container when they login, by switching
namespaces.
%endif

%package devel
Summary: Libraries, includes, etc. to compile with the libvirt library
Group: Development/Libraries
Requires: %{name}-client = %{version}-%{release}
Requires: %{name}-docs = %{version}-%{release}
Requires: pkgconfig

%description devel
Include header files & development libraries for the libvirt C library.

%if %{with_sanlock}
%package lock-sanlock
Summary: Sanlock lock manager plugin for QEMU driver
Group: Development/Libraries
    %if 0%{?fedora} >= 17 || 0%{?rhel} >= 6
Requires: sanlock >= 2.4
    %else
Requires: sanlock >= 1.8
    %endif
#for virt-sanlock-cleanup require augeas
Requires: augeas
Requires: %{name}-daemon = %{version}-%{release}
Requires: %{name}-client = %{version}-%{release}

%description lock-sanlock
Includes the Sanlock lock manager plugin for the QEMU
driver
%endif


%prep
%setup -q

# Patches have to be stored in a temporary file because RPM has
# a limit on the length of the result of any macro expansion;
# if the string is longer, it's silently cropped
%{lua:
    tmp = os.tmpname();
    f = io.open(tmp, "w+");
    count = 0;
    for i, p in ipairs(patches) do
        f:write(p.."\n");
        count = count + 1;
    end;
    f:close();
    print("PATCHCOUNT="..count.."\n")
    print("PATCHLIST="..tmp.."\n")
}

git init -q
git config user.name rpm-build
git config user.email rpm-build
git config gc.auto 0
git add .
git commit -q -a --author 'rpm-build <rpm-build>' \
           -m '%{name}-%{version} base'

COUNT=$(grep '\.patch$' $PATCHLIST | wc -l)
if [ $COUNT -ne $PATCHCOUNT ]; then
    echo "Found $COUNT patches in $PATCHLIST, expected $PATCHCOUNT"
    exit 1
fi
if [ $COUNT -gt 0 ]; then
    xargs git am <$PATCHLIST || exit 1
fi
echo "Applied $COUNT patches"
rm -f $PATCHLIST

%build
%if ! %{with_xen}
    %define _without_xen --without-xen
%endif

%if ! %{with_qemu}
    %define _without_qemu --without-qemu
%endif

%if ! %{with_openvz}
    %define _without_openvz --without-openvz
%endif

%if ! %{with_lxc}
    %define _without_lxc --without-lxc
%endif

%if ! %{with_vbox}
    %define _without_vbox --without-vbox
%endif

%if ! %{with_xenapi}
    %define _without_xenapi --without-xenapi
%endif

%if ! %{with_libxl}
    %define _without_libxl --without-libxl
%endif

%if ! %{with_sasl}
    %define _without_sasl --without-sasl
%endif

%if ! %{with_avahi}
    %define _without_avahi --without-avahi
%endif

%if ! %{with_phyp}
    %define _without_phyp --without-phyp
%endif

%if ! %{with_esx}
    %define _without_esx --without-esx
%endif

%if ! %{with_hyperv}
    %define _without_hyperv --without-hyperv
%endif

%if ! %{with_vmware}
    %define _without_vmware --without-vmware
%endif

%if ! %{with_vz}
    %define _without_vz --without-vz
%endif

%if ! %{with_polkit}
    %define _without_polkit --without-polkit
%endif

%if ! %{with_libvirtd}
    %define _without_libvirtd --without-libvirtd
%endif

%if ! %{with_uml}
    %define _without_uml --without-uml
%endif

%if %{with_rhel5}
    %define _with_rhel5_api --with-rhel5-api
%endif

%if ! %{with_interface}
    %define _without_interface --without-interface
%endif

%if ! %{with_network}
    %define _without_network --without-network
%endif

%if ! %{with_storage_fs}
    %define _without_storage_fs --without-storage-fs
%endif

%if ! %{with_storage_lvm}
    %define _without_storage_lvm --without-storage-lvm
%endif

%if ! %{with_storage_iscsi}
    %define _without_storage_iscsi --without-storage-iscsi
%endif

%if ! %{with_storage_disk}
    %define _without_storage_disk --without-storage-disk
%endif

%if ! %{with_storage_mpath}
    %define _without_storage_mpath --without-storage-mpath
%endif

%if ! %{with_storage_rbd}
    %define _without_storage_rbd --without-storage-rbd
%endif

%if ! %{with_storage_sheepdog}
    %define _without_storage_sheepdog --without-storage-sheepdog
%endif

%if ! %{with_storage_gluster}
    %define _without_storage_gluster --without-storage-gluster
%endif

%if ! %{with_numactl}
    %define _without_numactl --without-numactl
%endif

%if ! %{with_numad}
    %define _without_numad --without-numad
%endif

%if ! %{with_capng}
    %define _without_capng --without-capng
%endif

%if ! %{with_fuse}
    %define _without_fuse --without-fuse
%endif

%if ! %{with_netcf}
    %define _without_netcf --without-netcf
%endif

%if ! %{with_selinux}
    %define _without_selinux --without-selinux
%endif

%if ! %{with_apparmor}
    %define _without_apparmor --without-apparmor
%endif

%if ! %{with_hal}
    %define _without_hal --without-hal
%endif

%if ! %{with_udev}
    %define _without_udev --without-udev
%endif

%if ! %{with_yajl}
    %define _without_yajl --without-yajl
%endif

%if ! %{with_sanlock}
    %define _without_sanlock --without-sanlock
%endif

%if ! %{with_libpcap}
    %define _without_libpcap --without-libpcap
%endif

%if ! %{with_macvtap}
    %define _without_macvtap --without-macvtap
%endif

%if ! %{with_audit}
    %define _without_audit --without-audit
%endif

%if ! %{with_dtrace}
    %define _without_dtrace --without-dtrace
%endif

%if ! %{with_driver_modules}
    %define _without_driver_modules --without-driver-modules
%endif

%if %{with_firewalld}
    %define _with_firewalld --with-firewalld
%endif

%if ! %{with_wireshark}
    %define _without_wireshark --without-wireshark-dissector
%endif

%if ! %{with_systemd_daemon}
    %define _without_systemd_daemon --without-systemd-daemon
%endif

%if ! %{with_pm_utils}
    %define _without_pm_utils --without-pm-utils
%endif

%define when  %(date +"%%F-%%T")
%define where %(hostname)
%define who   %{?packager}%{!?packager:Unknown}
%define with_packager --with-packager="%{who}, %{when}, %{where}"
%define with_packager_version --with-packager-version="%{release}"

%if %{with_systemd}
    %define init_scripts --with-init_script=systemd
%else
    %define init_scripts --with-init_script=redhat
%endif

%if %{with_selinux}
    %if 0%{?fedora} >= 17 || 0%{?rhel} >= 7
        %define with_selinux_mount --with-selinux-mount="/sys/fs/selinux"
    %else
        %define with_selinux_mount --with-selinux-mount="/selinux"
    %endif
%endif

# place macros above and build commands below this comment

%if 0%{?enable_autotools}
 autoreconf -if
%endif

rm -f po/stamp-po
%configure %{?_without_xen} \
           %{?_without_qemu} \
           %{?_without_openvz} \
           %{?_without_lxc} \
           %{?_without_vbox} \
           %{?_without_libxl} \
           %{?_without_xenapi} \
           %{?_without_sasl} \
           %{?_without_avahi} \
           %{?_without_polkit} \
           %{?_without_libvirtd} \
           %{?_without_uml} \
           %{?_without_phyp} \
           %{?_without_esx} \
           %{?_without_hyperv} \
           %{?_without_vmware} \
           %{?_without_vz} \
           --without-bhyve \
           %{?_without_interface} \
           %{?_without_network} \
           %{?_with_rhel5_api} \
           %{?_without_storage_fs} \
           %{?_without_storage_lvm} \
           %{?_without_storage_iscsi} \
           %{?_without_storage_disk} \
           %{?_without_storage_mpath} \
           %{?_without_storage_rbd} \
           %{?_without_storage_sheepdog} \
           %{?_without_storage_gluster} \
           %{?_without_numactl} \
           %{?_without_numad} \
           %{?_without_capng} \
           %{?_without_fuse} \
           %{?_without_netcf} \
           %{?_without_selinux} \
           %{?_with_selinux_mount} \
           %{?_without_apparmor} \
           %{?_without_hal} \
           %{?_without_udev} \
           %{?_without_yajl} \
           %{?_without_sanlock} \
           %{?_without_libpcap} \
           %{?_without_macvtap} \
           %{?_without_audit} \
           %{?_without_dtrace} \
           %{?_without_driver_modules} \
           %{?_with_firewalld} \
           %{?_without_wireshark} \
           %{?_without_systemd_daemon} \
           %{?_without_pm_utils} \
           %{with_packager} \
           %{with_packager_version} \
           --with-qemu-user=%{qemu_user} \
           --with-qemu-group=%{qemu_group} \
           %{?with_loader_nvram} \
           %{?enable_werror} \
           --enable-expensive-tests \
           %{init_scripts}
make %{?_smp_mflags}
gzip -9 ChangeLog

%install
rm -fr %{buildroot}

# Avoid using makeinstall macro as it changes prefixes rather than setting
# DESTDIR. Newer make_install macro would be better but it's not available
# on RHEL 5, thus we need to expand it here.
make install DESTDIR=%{?buildroot} SYSTEMD_UNIT_DIR=%{_unitdir}

for i in object-events dominfo domsuspend hellolibvirt openauth xml/nwfilter systemtap dommigrate domtop
do
  (cd examples/$i ; make clean ; rm -rf .deps .libs Makefile Makefile.in)
done
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/lock-driver/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/lock-driver/*.a
%if %{with_driver_modules}
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/connection-driver/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt/connection-driver/*.a
%endif
%if %{with_wireshark}
rm -f $RPM_BUILD_ROOT%{_libdir}/wireshark/plugins/*/libvirt.la
%endif

# Temporarily get rid of not-installed libvirt-admin.so
rm -f $RPM_BUILD_ROOT%{_libdir}/libvirt-admin.so

%if %{with_network}
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/lib/libvirt/dnsmasq/
# We don't want to install /etc/libvirt/qemu/networks in the main %files list
# because if the admin wants to delete the default network completely, we don't
# want to end up re-incarnating it on every RPM upgrade.
install -d -m 0755 $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/
cp $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml \
   $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/default.xml
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml
# Strip auto-generated UUID - we need it generated per-install
sed -i -e "/<uuid>/d" $RPM_BUILD_ROOT%{_datadir}/libvirt/networks/default.xml
%else
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/default.xml
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml
%endif
%if ! %{with_qemu}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_qemu.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
%endif
%find_lang %{name}

%if ! %{with_sanlock}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirt_sanlock.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
%endif

%if ! %{with_lxc}
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_lxc.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%endif

%if ! %{with_qemu}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/qemu.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.qemu
%endif
%if ! %{with_lxc}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/lxc.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.lxc
%endif
%if ! %{with_libxl}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/libvirt/libxl.conf
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.libxl
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/libvirtd_libxl.aug
rm -f $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
%endif
%if ! %{with_uml}
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/libvirtd.uml
%endif

# Copied into libvirt-docs subpackage eventually
mv $RPM_BUILD_ROOT%{_datadir}/doc/libvirt-%{version} libvirt-docs

%if %{with_dtrace}
    %ifarch %{power64} s390x x86_64 ia64 alpha sparc64
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_probes-64.stp
mv $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes.stp \
   $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/libvirt_qemu_probes-64.stp
    %endif
%endif

%if 0%{?rhel} == 5
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/sysctl.d/60-libvirtd.conf
%endif

%clean
rm -fr %{buildroot}

%check
cd tests
make
# These tests don't current work in a mock build root
for i in nodeinfotest seclabeltest
do
  rm -f $i
  printf 'int main(void) { return 0; }' > $i.c
  printf '#!/bin/sh\nexit 0\n' > $i
  chmod +x $i
done
if ! make check VIR_TEST_DEBUG=1
then
  cat test-suite.log || true
  exit 1
fi

%if %{with_libvirtd}
%pre daemon
    %if ! %{with_driver_modules}
        %if %{with_qemu}
            %if 0%{?fedora} || 0%{?rhel} >= 6
# We want soft static allocation of well-known ids, as disk images
# are commonly shared across NFS mounts by id rather than name; see
# https://fedoraproject.org/wiki/Packaging:UsersAndGroups
getent group kvm >/dev/null || groupadd -f -g 36 -r kvm
getent group qemu >/dev/null || groupadd -f -g 107 -r qemu
if ! getent passwd qemu >/dev/null; then
  if ! getent passwd 107 >/dev/null; then
    useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  else
    useradd -r -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  fi
fi
            %endif
        %endif
    %endif

    %if %{with_polkit}
        %if 0%{?fedora} || 0%{?rhel} >= 6
# 'libvirt' group is just to allow password-less polkit access to
# libvirtd. The uid number is irrelevant, so we use dynamic allocation
# described at the above link.
getent group libvirt >/dev/null || groupadd -r libvirt
        %endif
    %endif

exit 0

%post daemon

    %if %{with_systemd}
        %if %{with_systemd_macros}
            %systemd_post virtlockd.socket libvirtd.service libvirtd.socket
        %else
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl enable \
        virtlockd.socket \
        libvirtd.service >/dev/null 2>&1 || :
fi
        %endif
    %else
        %if %{with_cgconfig}
# Starting with Fedora 16/RHEL-7, systemd automounts all cgroups,
# and cgconfig is no longer a necessary service.
            %if (0%{?rhel} && 0%{?rhel} < 7) || (0%{?fedora} && 0%{?fedora} < 16)
if [ "$1" -eq "1" ]; then
/sbin/chkconfig cgconfig on
fi
            %endif
        %endif

/sbin/chkconfig --add libvirtd
/sbin/chkconfig --add virtlockd
    %endif

%preun daemon
    %if %{with_systemd}
        %if %{with_systemd_macros}
            %systemd_preun libvirtd.socket libvirtd.service virtlockd.socket virtlockd.service
        %else
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable \
        libvirtd.socket \
        libvirtd.service \
        virtlockd.socket \
        virtlockd.service > /dev/null 2>&1 || :
    /bin/systemctl stop \
        libvirtd.socket \
        libvirtd.service \
        virtlockd.socket \
        virtlockd.service > /dev/null 2>&1 || :
fi
        %endif
    %else
if [ $1 = 0 ]; then
    /sbin/service libvirtd stop 1>/dev/null 2>&1
    /sbin/chkconfig --del libvirtd
    /sbin/service virtlockd stop 1>/dev/null 2>&1
    /sbin/chkconfig --del virtlockd
fi
    %endif

%postun daemon
    %if %{with_systemd}
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    /bin/systemctl reload-or-try-restart virtlockd.service >/dev/null 2>&1 || :
    /bin/systemctl try-restart libvirtd.service >/dev/null 2>&1 || :
fi
    %else
if [ $1 -ge 1 ]; then
    /sbin/service virtlockd reload > /dev/null 2>&1 || :
    /sbin/service libvirtd condrestart > /dev/null 2>&1
fi
    %endif

    %if %{with_systemd}
    %else
%triggerpostun daemon -- libvirt-daemon < 1.2.1
if [ "$1" -ge "1" ]; then
    /sbin/service virtlockd reload > /dev/null 2>&1 || :
    /sbin/service libvirtd condrestart > /dev/null 2>&1
fi
    %endif

    %if %{with_network}
%post daemon-config-network
if test $1 -eq 1 && test ! -f %{_sysconfdir}/libvirt/qemu/networks/default.xml ; then
    # see if the network used by default network creates a conflict,
    # and try to resolve it
    # NB: 192.168.122.0/24 is used in the default.xml template file;
    # do not modify any of those values here without also modifying
    # them in the template.
    orig_sub=122
    sub=${orig_sub}
    nl='
'
    routes="${nl}$(ip route show | cut -d' ' -f1)${nl}"
    case ${routes} in
      *"${nl}192.168.${orig_sub}.0/24${nl}"*)
        # there was a match, so we need to look for an unused subnet
        for new_sub in $(seq 124 254); do
          case ${routes} in
          *"${nl}192.168.${new_sub}.0/24${nl}"*)
            ;;
          *)
            sub=$new_sub
            break;
            ;;
          esac
        done
        ;;
      *)
        ;;
    esac

    UUID=`/usr/bin/uuidgen`
    sed -e "s/${orig_sub}/${sub}/g" \
        -e "s,</name>,</name>\n  <uuid>$UUID</uuid>," \
         < %{_datadir}/libvirt/networks/default.xml \
         > %{_sysconfdir}/libvirt/qemu/networks/default.xml
    ln -s ../default.xml %{_sysconfdir}/libvirt/qemu/networks/autostart/default.xml
fi
    %endif

    %if %{with_systemd}
%triggerun -- libvirt < 0.9.4
%{_bindir}/systemd-sysv-convert --save libvirtd >/dev/null 2>&1 ||:

# If the package is allowed to autostart:
/bin/systemctl --no-reload enable libvirtd.service >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del libvirtd >/dev/null 2>&1 || :
/bin/systemctl try-restart libvirtd.service >/dev/null 2>&1 || :
    %endif

    %if %{with_driver_modules}
        %if %{with_qemu}
%pre daemon-driver-qemu
            %if 0%{?fedora} || 0%{?rhel} >= 6
# We want soft static allocation of well-known ids, as disk images
# are commonly shared across NFS mounts by id rather than name; see
# https://fedoraproject.org/wiki/Packaging:UsersAndGroups
getent group kvm >/dev/null || groupadd -f -g 36 -r kvm
getent group qemu >/dev/null || groupadd -f -g 107 -r qemu
if ! getent passwd qemu >/dev/null; then
  if ! getent passwd 107 >/dev/null; then
    useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  else
    useradd -r -g qemu -G kvm -d / -s /sbin/nologin -c "qemu user" qemu
  fi
fi
exit 0
            %endif
        %endif
    %endif
%endif # %{with_libvirtd}

%preun client

%if %{with_systemd}
    %if %{with_systemd_macros}
        %systemd_preun libvirt-guests.service
    %endif
%else
if [ $1 = 0 ]; then
    /sbin/chkconfig --del libvirt-guests
    rm -f /var/lib/libvirt/libvirt-guests
fi
%endif

%post client

/sbin/ldconfig
%if %{with_systemd}
    %if %{with_systemd_macros}
        %systemd_post libvirt-guests.service
    %endif
%else
/sbin/chkconfig --add libvirt-guests
%endif

%postun client

/sbin/ldconfig
%if %{with_systemd}
    %if %{with_systemd_macros}
        %systemd_postun libvirt-guests.service
    %endif
%triggerun client -- libvirt < 0.9.4
%{_bindir}/systemd-sysv-convert --save libvirt-guests >/dev/null 2>&1 ||:

# If the package is allowed to autostart:
/bin/systemctl --no-reload enable libvirt-guests.service >/dev/null 2>&1 ||:

# Run this because the SysV package being removed won't do them
/sbin/chkconfig --del libvirt-guests >/dev/null 2>&1 || :
%endif

%if %{with_sanlock}
%post lock-sanlock
if getent group sanlock > /dev/null ; then
    chmod 0770 %{_localstatedir}/lib/libvirt/sanlock
    chown root:sanlock %{_localstatedir}/lib/libvirt/sanlock
fi
%endif

%if %{with_lxc}
%pre login-shell
getent group virtlogin >/dev/null || groupadd -r virtlogin
exit 0
%endif

%files
%defattr(-, root, root)

%files docs
%defattr(-, root, root)
%doc AUTHORS ChangeLog.gz NEWS README TODO libvirt-docs/*

# API docs
%dir %{_datadir}/gtk-doc/html/libvirt/
%doc %{_datadir}/gtk-doc/html/libvirt/*.devhelp
%doc %{_datadir}/gtk-doc/html/libvirt/*.html
%doc %{_datadir}/gtk-doc/html/libvirt/*.png
%doc %{_datadir}/gtk-doc/html/libvirt/*.css

%if %{with_libvirtd}
%files daemon
%defattr(-, root, root)

%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/

    %if %{with_systemd}
%{_unitdir}/libvirtd.service
%{_unitdir}/libvirtd.socket
%{_unitdir}/virtlockd.service
%{_unitdir}/virtlockd.socket
    %else
%{_sysconfdir}/rc.d/init.d/libvirtd
%{_sysconfdir}/rc.d/init.d/virtlockd
    %endif
%doc daemon/libvirtd.upstart
%config(noreplace) %{_sysconfdir}/sysconfig/libvirtd
%config(noreplace) %{_sysconfdir}/sysconfig/virtlockd
%config(noreplace) %{_sysconfdir}/libvirt/libvirtd.conf
%config(noreplace) %{_sysconfdir}/libvirt/virtlockd.conf
    %if 0%{?fedora} || 0%{?rhel} >= 6
%config(noreplace) %{_prefix}/lib/sysctl.d/60-libvirtd.conf
    %endif

%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd
%dir %{_datadir}/libvirt/

%ghost %dir %{_localstatedir}/run/libvirt/

%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/images/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/filesystems/
%dir %attr(0711, root, root) %{_localstatedir}/lib/libvirt/boot/
%dir %attr(0711, root, root) %{_localstatedir}/cache/libvirt/


%dir %attr(0755, root, root) %{_libdir}/libvirt/lock-driver
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/lockd.so

%{_datadir}/augeas/lenses/libvirtd.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd.aug
%{_datadir}/augeas/lenses/virtlockd.aug
%{_datadir}/augeas/lenses/tests/test_virtlockd.aug
%{_datadir}/augeas/lenses/libvirt_lockd.aug
    %if %{with_qemu}
%{_datadir}/augeas/lenses/tests/test_libvirt_lockd.aug
    %endif

    %if %{with_polkit}
        %if 0%{?fedora} || 0%{?rhel} >= 6
%{_datadir}/polkit-1/actions/org.libvirt.unix.policy
%{_datadir}/polkit-1/actions/org.libvirt.api.policy
%{_datadir}/polkit-1/rules.d/50-libvirt.rules
        %else
%{_datadir}/PolicyKit/policy/org.libvirt.unix.policy
        %endif
    %endif

%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/

%attr(0755, root, root) %{_libexecdir}/libvirt_iohelper

    %if %{with_apparmor}
%attr(0755, root, root) %{_libexecdir}/virt-aa-helper
    %endif

%attr(0755, root, root) %{_sbindir}/libvirtd
%attr(0755, root, root) %{_sbindir}/virtlockd

%{_mandir}/man8/libvirtd.8*
%{_mandir}/man8/virtlockd.8*

    %if ! %{with_driver_modules}
        %if %{with_network} || %{with_qemu}
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
        %endif
        %if %{with_network} || %{with_nwfilter}
%ghost %dir %{_localstatedir}/run/libvirt/network/
        %endif
        %if %{with_network}
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/autostart
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/network/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/dnsmasq/
%attr(0755, root, root) %{_libexecdir}/libvirt_leaseshelper
        %endif
        %if %{with_nwfilter}
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/nwfilter/
        %endif
        %if %{with_storage_disk}
%attr(0755, root, root) %{_libexecdir}/libvirt_parthelper
        %endif
        %if %{with_qemu}
%config(noreplace) %{_sysconfdir}/libvirt/qemu.conf
%config(noreplace) %{_sysconfdir}/libvirt/qemu-lockd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.qemu
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/qemu/
%ghost %dir %attr(0700, root, root) %{_localstatedir}/run/libvirt/qemu/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/
%dir %attr(0750, %{qemu_user}, %{qemu_group}) %{_localstatedir}/cache/libvirt/qemu/
%{_datadir}/augeas/lenses/libvirtd_qemu.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
        %endif
        %if %{with_lxc}
%config(noreplace) %{_sysconfdir}/libvirt/lxc.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.lxc
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/lxc/
%ghost %dir %{_localstatedir}/run/libvirt/lxc/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/lxc/
%{_datadir}/augeas/lenses/libvirtd_lxc.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%attr(0755, root, root) %{_libexecdir}/libvirt_lxc
        %endif
        %if %{with_uml}
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.uml
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/uml/
%ghost %dir %{_localstatedir}/run/libvirt/uml/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/uml/
        %endif
        %if %{with_libxl}
%config(noreplace) %{_sysconfdir}/libvirt/libxl.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.libxl
%config(noreplace) %{_sysconfdir}/libvirt/libxl-lockd.conf
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/libxl/
%ghost %dir %{_localstatedir}/run/libvirt/libxl/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/
%{_datadir}/augeas/lenses/libvirtd_libxl.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
        %endif
        %if %{with_xen}
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/xen/
        %endif
    %endif # ! %{with_driver_modules}

    %if %{with_network}

%doc examples/polkit/*.rules

%files daemon-config-network
%defattr(-, root, root)
%dir %{_datadir}/libvirt/networks/
%{_datadir}/libvirt/networks/default.xml
    %endif

    %if %{with_nwfilter}
%files daemon-config-nwfilter
%defattr(-, root, root)
%{_sysconfdir}/libvirt/nwfilter/*.xml
    %endif

    %if %{with_driver_modules}
        %if %{with_interface}
%files daemon-driver-interface
%defattr(-, root, root)
%{_libdir}/%{name}/connection-driver/libvirt_driver_interface.so
        %endif

        %if %{with_network}
%files daemon-driver-network
%defattr(-, root, root)
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/networks/autostart
%ghost %dir %{_localstatedir}/run/libvirt/network/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/network/
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/dnsmasq/
%attr(0755, root, root) %{_libexecdir}/libvirt_leaseshelper
%{_libdir}/%{name}/connection-driver/libvirt_driver_network.so
        %endif

        %if %{with_nodedev}
%files daemon-driver-nodedev
%defattr(-, root, root)
%{_libdir}/%{name}/connection-driver/libvirt_driver_nodedev.so
        %endif

        %if %{with_nwfilter}
%files daemon-driver-nwfilter
%defattr(-, root, root)
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/nwfilter/
%ghost %dir %{_localstatedir}/run/libvirt/network/
%{_libdir}/%{name}/connection-driver/libvirt_driver_nwfilter.so
        %endif

%files daemon-driver-secret
%defattr(-, root, root)
%{_libdir}/%{name}/connection-driver/libvirt_driver_secret.so

        %if %{with_storage}
%files daemon-driver-storage
%defattr(-, root, root)
            %if %{with_storage_disk}
%attr(0755, root, root) %{_libexecdir}/libvirt_parthelper
            %endif
%{_libdir}/%{name}/connection-driver/libvirt_driver_storage.so
        %endif

        %if %{with_qemu}
%files daemon-driver-qemu
%defattr(-, root, root)
%dir %attr(0700, root, root) %{_sysconfdir}/libvirt/qemu/
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/qemu/
%config(noreplace) %{_sysconfdir}/libvirt/qemu.conf
%config(noreplace) %{_sysconfdir}/libvirt/qemu-lockd.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.qemu
%ghost %dir %attr(0700, root, root) %{_localstatedir}/run/libvirt/qemu/
%dir %attr(0751, %{qemu_user}, %{qemu_group}) %{_localstatedir}/lib/libvirt/qemu/
%dir %attr(0750, %{qemu_user}, %{qemu_group}) %{_localstatedir}/cache/libvirt/qemu/
%{_datadir}/augeas/lenses/libvirtd_qemu.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_qemu.aug
%{_libdir}/%{name}/connection-driver/libvirt_driver_qemu.so
        %endif

        %if %{with_lxc}
%files daemon-driver-lxc
%defattr(-, root, root)
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/lxc/
%config(noreplace) %{_sysconfdir}/libvirt/lxc.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.lxc
%ghost %dir %{_localstatedir}/run/libvirt/lxc/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/lxc/
%{_datadir}/augeas/lenses/libvirtd_lxc.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_lxc.aug
%attr(0755, root, root) %{_libexecdir}/libvirt_lxc
%{_libdir}/%{name}/connection-driver/libvirt_driver_lxc.so
        %endif

        %if %{with_uml}
%files daemon-driver-uml
%defattr(-, root, root)
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/uml/
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.uml
%ghost %dir %{_localstatedir}/run/libvirt/uml/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/uml/
%{_libdir}/%{name}/connection-driver/libvirt_driver_uml.so
        %endif

        %if %{with_xen}
%files daemon-driver-xen
%defattr(-, root, root)
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/xen/
%{_libdir}/%{name}/connection-driver/libvirt_driver_xen.so
        %endif

        %if %{with_libxl}
%files daemon-driver-libxl
%defattr(-, root, root)
%config(noreplace) %{_sysconfdir}/libvirt/libxl.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/libvirtd.libxl
%config(noreplace) %{_sysconfdir}/libvirt/libxl-lockd.conf
%{_datadir}/augeas/lenses/libvirtd_libxl.aug
%{_datadir}/augeas/lenses/tests/test_libvirtd_libxl.aug
%dir %attr(0700, root, root) %{_localstatedir}/log/libvirt/libxl/
%ghost %dir %{_localstatedir}/run/libvirt/libxl/
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/libxl/
%{_libdir}/%{name}/connection-driver/libvirt_driver_libxl.so
        %endif

        %if %{with_vbox}
%files daemon-driver-vbox
%defattr(-, root, root)
%{_libdir}/%{name}/connection-driver/libvirt_driver_vbox.so
        %endif
    %endif # %{with_driver_modules}

    %if %{with_qemu_tcg}
%files daemon-qemu
%defattr(-, root, root)
    %endif

    %if %{with_qemu_kvm}
%files daemon-kvm
%defattr(-, root, root)
    %endif

    %if %{with_lxc}
%files daemon-lxc
%defattr(-, root, root)
    %endif

    %if %{with_uml}
%files daemon-uml
%defattr(-, root, root)
    %endif

    %if %{with_xen} || %{with_libxl}
%files daemon-xen
%defattr(-, root, root)
    %endif

    %if %{with_vbox}
%files daemon-vbox
%defattr(-, root, root)
    %endif
%endif # %{with_libvirtd}

%if %{with_sanlock}
%files lock-sanlock
%defattr(-, root, root)
    %if %{with_qemu}
%config(noreplace) %{_sysconfdir}/libvirt/qemu-sanlock.conf
    %endif
    %if %{with_libxl}
%config(noreplace) %{_sysconfdir}/libvirt/libxl-sanlock.conf
    %endif
%attr(0755, root, root) %{_libdir}/libvirt/lock-driver/sanlock.so
%{_datadir}/augeas/lenses/libvirt_sanlock.aug
%{_datadir}/augeas/lenses/tests/test_libvirt_sanlock.aug
%dir %attr(0700, root, root) %{_localstatedir}/lib/libvirt/sanlock
%{_sbindir}/virt-sanlock-cleanup
%{_mandir}/man8/virt-sanlock-cleanup.8*
%attr(0755, root, root) %{_libexecdir}/libvirt_sanlock_helper
%endif

%files client -f %{name}.lang
%defattr(-, root, root)
%doc COPYING COPYING.LESSER

%config(noreplace) %{_sysconfdir}/libvirt/libvirt.conf
%{_mandir}/man1/virsh.1*
%{_mandir}/man1/virt-xml-validate.1*
%{_mandir}/man1/virt-pki-validate.1*
%{_mandir}/man1/virt-host-validate.1*
%{_bindir}/virsh
%{_bindir}/virt-xml-validate
%{_bindir}/virt-pki-validate
%{_bindir}/virt-host-validate
%{_libdir}/libvirt.so.*
%{_libdir}/libvirt-qemu.so.*
%{_libdir}/libvirt-lxc.so.*
%{_libdir}/libvirt-admin.so.*

%if %{with_dtrace}
%{_datadir}/systemtap/tapset/libvirt_probes*.stp
%{_datadir}/systemtap/tapset/libvirt_qemu_probes*.stp
%{_datadir}/systemtap/tapset/libvirt_functions.stp
%endif

%dir %{_datadir}/libvirt/
%dir %{_datadir}/libvirt/schemas/

%{_datadir}/libvirt/schemas/basictypes.rng
%{_datadir}/libvirt/schemas/capability.rng
%{_datadir}/libvirt/schemas/domain.rng
%{_datadir}/libvirt/schemas/domaincaps.rng
%{_datadir}/libvirt/schemas/domaincommon.rng
%{_datadir}/libvirt/schemas/domainsnapshot.rng
%{_datadir}/libvirt/schemas/interface.rng
%{_datadir}/libvirt/schemas/network.rng
%{_datadir}/libvirt/schemas/networkcommon.rng
%{_datadir}/libvirt/schemas/nodedev.rng
%{_datadir}/libvirt/schemas/nwfilter.rng
%{_datadir}/libvirt/schemas/secret.rng
%{_datadir}/libvirt/schemas/storagecommon.rng
%{_datadir}/libvirt/schemas/storagepool.rng
%{_datadir}/libvirt/schemas/storagevol.rng

%{_datadir}/libvirt/cpu_map.xml
%{_datadir}/libvirt/libvirtLogo.png

%if %{with_systemd}
%{_unitdir}/libvirt-guests.service
%else
%{_sysconfdir}/rc.d/init.d/libvirt-guests
%endif
%config(noreplace) %{_sysconfdir}/sysconfig/libvirt-guests
%attr(0755, root, root) %{_libexecdir}/libvirt-guests.sh
%dir %attr(0755, root, root) %{_localstatedir}/lib/libvirt/

%if %{with_sasl}
%config(noreplace) %{_sysconfdir}/sasl2/libvirt.conf
%endif

%if %{with_wireshark}
%files wireshark
%{_libdir}/wireshark/plugins/*/libvirt.so
%endif

%if %{with_lxc}
%files login-shell
%attr(4750, root, virtlogin) %{_bindir}/virt-login-shell
%config(noreplace) %{_sysconfdir}/libvirt/virt-login-shell.conf
%{_mandir}/man1/virt-login-shell.1*
%endif

%files devel
%defattr(-, root, root)

%{_libdir}/libvirt.so
%{_libdir}/libvirt-qemu.so
%{_libdir}/libvirt-lxc.so
%dir %{_includedir}/libvirt
%{_includedir}/libvirt/virterror.h
%{_includedir}/libvirt/libvirt.h
%{_includedir}/libvirt/libvirt-domain.h
%{_includedir}/libvirt/libvirt-domain-snapshot.h
%{_includedir}/libvirt/libvirt-event.h
%{_includedir}/libvirt/libvirt-host.h
%{_includedir}/libvirt/libvirt-interface.h
%{_includedir}/libvirt/libvirt-network.h
%{_includedir}/libvirt/libvirt-nodedev.h
%{_includedir}/libvirt/libvirt-nwfilter.h
%{_includedir}/libvirt/libvirt-secret.h
%{_includedir}/libvirt/libvirt-storage.h
%{_includedir}/libvirt/libvirt-stream.h
%{_includedir}/libvirt/libvirt-qemu.h
%{_includedir}/libvirt/libvirt-lxc.h
%{_libdir}/pkgconfig/libvirt.pc
%{_libdir}/pkgconfig/libvirt-qemu.pc
%{_libdir}/pkgconfig/libvirt-lxc.pc

%dir %{_datadir}/libvirt/api/
%{_datadir}/libvirt/api/libvirt-api.xml
%{_datadir}/libvirt/api/libvirt-qemu-api.xml
%{_datadir}/libvirt/api/libvirt-lxc-api.xml


%doc docs/*.html docs/html docs/*.gif
%doc docs/libvirt-api.xml
%doc examples/hellolibvirt
%doc examples/object-events
%doc examples/dominfo
%doc examples/domsuspend
%doc examples/dommigrate
%doc examples/openauth
%doc examples/xml
%doc examples/systemtap

%changelog
* Mon Aug 29 2016 Yaowei Bai <baiyaowei@cmss.chinamobile.com> - 1.2.17-13.el7_2.5.1
- libvirt-qemu-agent-Fix-QEMU-guest-agent-is-not-available-due-to-an-error.patch

* Thu May 26 2016 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-13.el7_2.5
- nodedev: Indent PCI express for future fix (rhbz#1331328)
- nodedev: Expose PCI header type (rhbz#1331328)
- nodedev: Fix parsing of generated XMLs (rhbz#1331328)
- qemu: driver: Remove unnecessary flag in qemuDomainGetStatsBlock (rhbz#1339963)
- qemu: driver: Separate bulk stats worker for block devices (rhbz#1339963)
- qemu: bulk stats: Don't access possibly blocked storage (rhbz#1339963)

* Wed Mar  2 2016 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-13.el7_2.4
- systemd: Escape machine name for machined (rhbz#1308494)
- systemd: Add virSystemdGetMachineNameByPID (rhbz#1308494)
- systemd: Modernize machine naming (rhbz#1308494)
- virSystemdGetMachineNameByPID: Initialize @reply (rhbz#1308494)
- util: Fix virCgroupNewMachine ATTRIBUTE_NONNULL args (rhbz#1308494)
- dbus: Don't unref NULL messages (rhbz#1308494)
- vmx: Expose datacenter path in domain XML (rhbz#1305489)

* Wed Jan 27 2016 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-13.el7_2.3
- vmx: Adapt to emptyBackingString for cdrom-image (rhbz#1301892)

* Mon Nov 23 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-13.el7_2.2
- qemu: Support vhost-user-multiqueue with QEMU 2.3 (rhbz#1284416)

* Fri Nov 20 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-13.el7_2.1
- qemu: migration: Properly parse memory hotplug migration flag (rhbz#1280419)
- qemu: Emit correct audit message for memory hot unplug (rhbz#1280420)
- qemu: Emit correct audit message for memory hot plug (rhbz#1280420)
- qemu: Extract logic to determine the mlock limit size for VFIO (rhbz#1280420)
- qemu: hotplug: Fix mlock limit handling on memory hotplug (rhbz#1280420)
- qemu: domain: Restructurate control flow in qemuDomainGetMlockLimitBytes (rhbz#1280420)
- qemu: Explain mlock limit size more in detail (rhbz#1280420)
- qemu: hotplug: Reject VFIO hotplug if setting RLIMIT_MEMLOCK fails (rhbz#1283924)
- process: Log when limiting the amount of locked memory (rhbz#1283924)
- qemu: Use qemuDomainRequiresMlock() in qemuBuildCommandLine() (rhbz#1283924)
- qemu: Use qemuDomainRequiresMlock() when attaching PCI hostdev (rhbz#1283924)
- qemu: Add ppc64-specific math to qemuDomainGetMlockLimitBytes() (rhbz#1283924)
- qemu: Always set locked memory limit for ppc64 domains (rhbz#1283924)

* Thu Oct  8 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-13
- qemu: Add conditions for qemu-kvm use on ppc64 (rhbz#1267882)
- qemu: Move simplification variable to begining of the function (rhbz#1266856)
- qemu: Extract -mem-path building into its own function (rhbz#1266856)
- qemu: Add -mem-path even with numa (rhbz#1266856)
- qemu: Use memory-backing-file only when needed (rhbz#1266856)
- qemu: Always update migration times on destination (rhbz#1265902)
- qemu: Copy completed migration stats only on success (rhbz#1265902)
- qemu: Introduce flags in qemuMigrationCompleted (rhbz#1265902)
- qemu: Make updating stats in qemuMigrationCheckJobStatus optional (rhbz#1265902)
- qemu: Wait until destination QEMU consumes all migration data (rhbz#1265902)

* Wed Sep 30 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-12
- qemu: Fix dynamic_ownership qemu.conf setting (rhbz#1267154)

* Fri Sep 25 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-11
- domain: Fix migratable XML with graphics/@listen (rhbz#1265111)

* Wed Sep 23 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-10
- virSecuritySELinuxSetSecurityAllLabel: drop useless virFileIsSharedFSType (rhbz#1124841)
- security_selinux: Replace SELinuxSCSICallbackData with proper struct (rhbz#1124841)
- virSecurityManager: Track if running as privileged (rhbz#1124841)
- security_selinux: Take @privileged into account (rhbz#1124841)
- qemu: Fix using guest architecture as lookup key (rhbz#1260753)
- virfile: Check for existence of dir in virFileDeleteTree (rhbz#1146886)
- Revert "qemu: Fix integer/boolean logic in qemuSetUnprivSGIO" (rhbz#1072736)
- qemu: migration: Relax enforcement of memory hotplug support (rhbz#1252685)
- conf: Add helper to determine whether memory hotplug is enabled for a vm (rhbz#1252685)
- qemu: Make memory alignment helper more universal (rhbz#1252685)
- conf: Drop VIR_DOMAIN_DEF_PARSE_CLOCK_ADJUST flag (rhbz#1252685)
- conf: Document all VIR_DOMAIN_DEF_PARSE_* flags (rhbz#1252685)
- conf: Add XML parser flag that will allow us to do incompatible updates (rhbz#1252685)
- conf: Split memory related post parse stuff into separate function (rhbz#1252685)
- conf: Rename max_balloon to total_memory (rhbz#1252685)
- conf: Pre-calculate initial memory size instead of always calculating it (rhbz#1252685)
- conf: Don't always recalculate initial memory size from NUMA size totals (rhbz#1252685)
- qemu: command: Align memory sizes only on fresh starts (rhbz#1252685)
- qemu: ppc64: Align memory sizes to 256MiB blocks (rhbz#1249006)
- test: Add test to validate that memory sizes don't get updated on migration (rhbz#1252685)
- qemu: Align memory module sizes to 2MiB (rhbz#1252685)
- qemu: Refresh memory size only on fresh starts (rhbz#1242940)

* Wed Sep 16 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-9
- conf: fix crash when parsing a unordered NUMA <cell/> (rhbz#1260846)
- vmx: Some whitespace cleanup (rhbz#1172544)
- vmx: The virVMXParseDisk deviceType can be NULL, add some missing checks (rhbz#1172544)
- vmx: Add handling for CDROM devices with SCSI passthru (rhbz#1172544)
- qemu: hotplug: Properly clean up drive backend if frontend hotplug fails (rhbz#1262399)
- qemu: Introduce QEMU_CAPS_DEVICE_RTL8139 (rhbz#1254044)
- qemu: Introduce QEMU_CAPS_DEVICE_E1000 (rhbz#1254044)
- qemu: Introduce QEMU_CAPS_DEVICE_VIRTIO_NET (rhbz#1254044)
- qemu: Try several network devices when looking for a default (rhbz#1254044)
- qemu: Report error if per-VM directory cannot be created (rhbz#1146886)
- qemu: Do not allow others into per-VM subdirectories (rhbz#1146886)
- qemu: Allow others to browse /var/lib/libvirt/qemu (rhbz#1146886)

* Mon Sep  7 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-8
- util: make virNetDev(Replace|Restore)MacAddress public functions (rhbz#1257004)
- util: don't use netlink to save/set mac for macvtap+passthrough+802.1Qbh (rhbz#1257004)
- cpu: Introduce IvyBridge CPU model (rhbz#1254420)
- examples: Add example polkit ACL rules (rhbz#1115289)
- qemu: don't use initialized ret in qemuRemoveSharedDevice (rhbz#1072736)
- qemu: Introduce qemuDomainMachineIsS390CCW (rhbz#1258361)
- qemu: Need to check for machine.os when using ADDRESS_TYPE_CCW (rhbz#1258361)

* Thu Sep  3 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-7
- Start daemon only after filesystems are mounted (rhbz#1255228)
- virfile: Add error for root squash change mode failure (rhbz#1253609)
- virfile: Introduce virFileUnlink (rhbz#1253609)
- storage: Correct the 'mode' check (rhbz#1253609)
- storage: Handle failure from refreshVol (rhbz#1253609)
- util: Add virStringGetFirstWithPrefix (rhbz#1165580)
- util: Add virCgroupGetBlockDevString (rhbz#1165580)
- util: Add getters for cgroup block device I/O throttling (rhbz#1165580)
- lxc: Sync BlkioDevice values when setting them in cgroups (rhbz#1165580)
- qemu: Sync BlkioDevice values when setting them in cgroups (rhbz#1165580)
- Allow vfio hotplug of a device to the domain which owns the iommu (rhbz#1256486)
- hostdev: skip ACS check when using VFIO for device assignment (rhbz#1256486)
- docs: Clarify unprivileged sgio feature (rhbz#1072736)
- qemu: Introduce qemuIsSharedHostdev (rhbz#1072736)
- qemu: Introduce qemuGetHostdevPath (rhbz#1072736)
- qemu: Refactor qemuCheckSharedDisk to create qemuCheckUnprivSGIO (rhbz#1072736)
- qemu: Inline qemuGetHostdevPath (rhbz#1072736)
- qemu: Refactor qemuSetUnprivSGIO return values (rhbz#1072736)
- qemu: Fix integer/boolean logic in qemuSetUnprivSGIO (rhbz#1072736)
- RHEL: qemu: Add ability to set sgio values for hostdev (rhbz#1072736)
- RHEL: qemu: Add check for unpriv sgio for SCSI generic host device (rhbz#1072736)
- security_selinux: Use proper structure to access socket data (rhbz#1146886)
- security_dac: Label non-listening sockets (rhbz#1146886)
- security: Add virSecurityDomainSetDirLabel (rhbz#1146886)
- security_stack: Add SetDirLabel support (rhbz#1146886)
- security_selinux: Add SetDirLabel support (rhbz#1146886)
- security_dac: Add SetDirLabel support (rhbz#1146886)
- qemu: Fix access to auto-generated socket paths (rhbz#1146886)
- tests: Use qemuProcessPrepareMonitorChr in qemuxmlnstest (rhbz#1146886)
- qemu: Label correct per-VM path when starting (rhbz#1146886)
- selinux: fix compile errors (rhbz#1146886)
- conf: Add ioeventfd option for controllers (rhbz#1150484)
- qemu: Enable ioeventfd usage for virtio-scsi controllers (rhbz#1150484)

* Sat Aug 22 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-6
- api: Remove check on iothread_id arg in virDomainPinIOThread (rhbz#1251886)
- api: Adjust comment for virDomainAddIOThread (rhbz#1251886)
- qemu: Add check for invalid iothread_id in qemuDomainChgIOThread (rhbz#1251886)
- conf: Check for attach disk usage of iothread=0 (rhbz#1253108)
- virNetDevBandwidthUpdateRate: turn class_id into integer (rhbz#1252473)
- bridge_driver: Introduce networkBandwidthChangeAllowed (rhbz#1252473)
- bridge_driver: Introduce networkBandwidthUpdate (rhbz#1252473)
- qemuDomainSetInterfaceParameters: Use new functions to update bandwidth (rhbz#1252473)
- cpu: Don't update host-model guest CPUs on ppc64 (rhbz#1251927)
- cpu: Better support for ppc64 compatibility modes (rhbz#1251927)
- cpu: Move check for NULL CPU model inside the driver (rhbz#1251927)
- tests: Add some compatibility-related cases to the CPU tests (rhbz#1251927)

* Thu Aug 13 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-5
- numa_conf: Introduce virDomainNumaGetMaxCPUID (rhbz#1176020)
- virDomainDefParseXML: Check for malicious cpu ids in <numa/> (rhbz#1176020)
- conf: more useful error message when pci function is out of range (rhbz#1004596)
- qemu: Fix reporting of physical capacity for block devices (rhbz#1250982)
- network: verify proper address family in updates to <host> and <range> (rhbz#1184736)
- rpc: Remove keepalive_required option (rhbz#1247087)
- virNetDevBandwidthParseRate: Reject negative values (rhbz#1022292)
- domain: Fix crash if trying to live update disk <serial> (rhbz#1007228)
- qemu: fail on attempts to use <filterref> for non-tap network connections (rhbz#1180011)
- network: validate network NAT range (rhbz#985653)
- conf: Don't try formating non-existing addresses (rhbz#985653)
- cpu: Rename {powerpc, ppc} => ppc64 (filesystem) (rhbz#1250977)
- cpu: Rename {powerpc, ppc} => ppc64 (exported symbols) (rhbz#1250977)
- cpu: Rename {powerpc, ppc} => ppc64 (internal symbols) (rhbz#1250977)
- cpu: Indentation changes in the ppc64 driver (rhbz#1250977)
- cpu: Mark driver functions in ppc64 driver (rhbz#1250977)
- cpu: Simplify NULL handling in ppc64 driver (rhbz#1250977)
- cpu: Simplify ppc64ModelFromCPU() (rhbz#1250977)
- cpu: Reorder functions in the ppc64 driver (rhbz#1250977)
- cpu: Remove ISA information from CPU map XML (rhbz#1250977)
- tests: Remove unused file (rhbz#1250977)
- tests: Improve result handling in cpuTestGuestData() (rhbz#1250977)
- cpu: Never skip CPU model name check in ppc64 driver (rhbz#1250977)
- cpu: CPU model names have to match on ppc64 (rhbz#1250977)
- cpu: Use ppc64Compute() to implement ppc64DriverCompare() (rhbz#1250977)
- tests: Temporarily disable ppc64 cpu tests (rhbz#1250977)
- cpu: Align ppc64 CPU data with x86 (rhbz#1250977)
- cpu: Support multiple PVRs in the ppc64 driver (rhbz#1250977)
- cpu: Simplify ppc64 part of CPU map XML (rhbz#1250977)
- cpu: Parse and use PVR masks in the ppc64 driver (rhbz#1250977)
- cpu: Add POWER8NVL information to CPU map XML (rhbz#1250977)
- cpu: Implement backwards compatibility in the ppc64 driver (rhbz#1250977)
- cpu: Forbid model fallback in the ppc64 driver (rhbz#1250977)
- tests: Re-enable ppc64 cpu tests (rhbz#1250977)
- tests: Add a bunch of cpu test case for ppc64 (rhbz#1250977)
- cpu: Fix segfault in the ppc64 driver (rhbz#1250977)
- qemu: Fix segfault when parsing private domain data (rhbz#1162947)
- conf: Pass private data to Parse function of XML options (rhbz#1162947)
- qemu: Keep numad hint after daemon restart (rhbz#1162947)
- qemu: Use numad information when getting pin information (rhbz#1162947)

* Fri Aug  7 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-4
- qemu: Reject migration with memory-hotplug if destination doesn't support it (rhbz#1248350)
- qemu: Properly check for incoming migration job (rhbz#1242904)
- qemu: Do not reset labels when migration fails (rhbz#1242904)
- qemu: Check for iotune_max support properly (rhbz#1224053)
- docs: Add Fibre Channel NPIV supported option for volume lun config (rhbz#1238545)
- conf: Allow error reporting in virDomainDiskSourceIsBlockType (rhbz#1238545)
- qemu: Forbid image pre-creation for non-shared storage migration (rhbz#1249587)
- qemu: remove deadcode in qemuDomain{HelperGetVcpus|GetIOThreadsLive} (rhbz#1213713)
- nodeinfo: Introduce local linuxGetCPUPresentPath (rhbz#1213713)
- nodeinfo: Add sysfs_prefix to nodeGetCPUCount (rhbz#1213713)
- nodeinfo: Add sysfs_prefix to nodeGetPresentCPUBitmap (rhbz#1213713)
- nodeinfo: Add sysfs_prefix to nodeGetCPUBitmap (rhbz#1213713)
- nodeinfo: Add sysfs_prefix to nodeGetCPUMap (rhbz#1213713)
- nodeinfo: Add sysfs_prefix to nodeGetInfo (rhbz#1213713)
- nodeinfo: Add sysfs_prefix to nodeCapsInitNUMA (rhbz#1213713)
- nodeinfo: Add sysfs_prefix to nodeGetMemoryStats (rhbz#1213713)
- nodeinfo: fix to parse present cpus rather than possible cpus (rhbz#1213713)
- tests: Add nodeinfo test for non-present CPUs (rhbz#1213713)
- nodeinfo: Make sysfs_prefix usage more consistent (rhbz#1213713)
- nodeinfo: Formatting changes (rhbz#1213713)
- tests: Restore links in deconfigured-cpus nodeinfo test (rhbz#1213713)
- nodeinfo: Add nodeGetPresentCPUBitmap() to libvirt_private.syms (rhbz#1213713)
- nodeinfo: Fix nodeGetCPUBitmap()'s fallback code path (rhbz#1213713)
- nodeinfo: Introduce linuxGetCPUGlobalPath() (rhbz#1213713)
- nodeinfo: Introduce linuxGetCPUOnlinePath() (rhbz#1213713)
- nodeinfo: Rename linuxParseCPUmax() to linuxParseCPUCount() (rhbz#1213713)
- nodeinfo: Add old kernel compatibility to nodeGetPresentCPUBitmap() (rhbz#1213713)
- nodeinfo: Remove out parameter from nodeGetCPUBitmap() (rhbz#1213713)
- nodeinfo: Rename nodeGetCPUBitmap() to nodeGetOnlineCPUBitmap() (rhbz#1213713)
- nodeinfo: Phase out cpu_set_t usage (rhbz#1213713)
- nodeinfo: Use nodeGetOnlineCPUBitmap() when parsing node (rhbz#1213713)
- nodeinfo: Use a bitmap to keep track of node CPUs (rhbz#1213713)
- nodeinfo: Calculate present and online CPUs only once (rhbz#1213713)
- nodeinfo: Check for errors when reading core_id (rhbz#1213713)
- Renamed deconfigured-cpus to allow make dist (rhbz#1213713)
- tests: Finish rename of the long nodeinfo test case (rhbz#1213713)
- nodeinfo: Fix output on PPC64 KVM hosts (rhbz#1213713)
- tests: Prepare for subcore tests (rhbz#1213713)
- tests: Add subcores1 nodeinfo test (rhbz#1213713)
- tests: Add subcores2 nodeinfo test (rhbz#1213713)
- tests: Add subcores3 nodeinfo test (rhbz#1213713)
- nodeinfo: Fix build failure when KVM headers are not available (rhbz#1213713)
- qemu: fix some api cannot work when disable cpuset in conf (rhbz#1244664)
- qemu: Auto assign pci addresses for shared memory devices (rhbz#1165029)
- conf: Add getter for network routes (rhbz#1094205)
- network: Add another collision check into networkCheckRouteCollision (rhbz#1094205)
- docs: Document how libvirt handles companion controllers (rhbz#1069590)
- qemu: Reject updating unsupported disk information (rhbz#1007228)

* Thu Jul 30 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-3
- qemuProcessHandleMigrationStatus: Update migration status more frequently (rhbz#1212077)
- qemuDomainSetNumaParamsLive: Check for NUMA mode more wisely (rhbz#1232663)
- qemu: process: Improve update of maximum balloon state at startup (rhbz#1242940)
- storage: Fix pool building when directory already exists (rhbz#1244080)
- virsh: report error if vcpu number exceed the guest maxvcpu number (rhbz#1160559)
- cmdVcpuPin: Remove dead code (rhbz#1160559)
- rpc: Add virNetDaemonHasClients (rhbz#1240283)
- rpc: Rework timerActive logic in daemon (rhbz#1240283)
- cgroup: Drop resource partition from virSystemdMakeScopeName (rhbz#1238570)
- virsh: blockjob: Extract block job info code into a separate function (rhbz#1227551)
- virsh: cmdBlockJob: Switch to declarative flag interlocking (rhbz#1227551)
- virsh: blockjob: Split out vshBlockJobSetSpeed from blockJobImpl (rhbz#1227551)
- virsh: block job: separate abort from blockJobImpl (rhbz#1227551)
- virsh: Split out block pull implementation from blockJobImpl (rhbz#1227551)
- virsh: Kill blockJobImpl by moving the final impl into cmdBlockCommit (rhbz#1227551)
- virsh: Refactor argument checking in cmdBlockCommit (rhbz#1227551)
- virsh: Refactor argument handling in cmdBlockCopy (rhbz#1227551)
- virsh: Refactor argument handling in cmdBlockPull (rhbz#1227551)
- qemu: Update state of block job to READY only if it actually is ready (rhbz#1227551)
- virsh: Refactor block job waiting in cmdBlockPull (rhbz#1227551)
- virsh: Refactor block job waiting in cmdBlockCommit (rhbz#1227551)
- virsh: Refactor block job waiting in cmdBlockCopy (rhbz#1197592)

* Fri Jul 10 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-2
- util: bitmap: Don't alloc overly large binary bitmaps (rhbz#1238589)
- storage: Fix regression in storagePoolUpdateAllState (rhbz#1238610)
- Separate isa-fdc options generation (rhbz#1227880)
- Explicitly format the isa-fdc controller for newer q35 machines (rhbz#1227880)
- Add rhel machine types to qemuDomainMachineNeedsFDC (rhbz#1227880)
- conf: Don't allow duplicated target names regardless of bus (rhbz#1142631)
- storage: Revert volume obj list updating after volume creation (4749d82a) (rhbz#1241454)
- qemu_monitor: Wire up MIGRATION event (rhbz#1212077)
- qemu: Enable migration events on QMP monitor (rhbz#1212077)
- qemuDomainGetJobStatsInternal: Support migration events (rhbz#1212077)
- qemu: Update migration state according to MIGRATION event (rhbz#1212077)
- qemu: Wait for migration events on domain condition (rhbz#1212077)
- qemu: Check duplicate WWNs also for hotplugged disks (rhbz#1208009)
- qemu: move the guest status check before agent config and status check (rhbz#1240979)
- qemu: report error for non-existing disk in blockjobinfo (rhbz#1241355)
- virCondWaitUntil: add another return value (rhbz#1147471)
- virDomainObjSignal: drop this function (rhbz#1147471)
- monitor: detect that eject fails because the tray is locked (rhbz#1147471)
- qemu_hotplug: try harder to eject media (rhbz#1147471)
- qemu: Drop LFs at the end of error from QEMU log (rhbz#1090093)
- Introduce virHashAtomic (rhbz#1090093)
- Introduce virErrorCopyNew (rhbz#1090093)
- RHEL: spec: Require perl-XML-XPath (rhbz#1090093)
- qemu: Remember incoming migration errors (rhbz#1090093)
- qemu: Don't report false error from MigrateFinish (rhbz#1090093)
- qemu: Use error from Finish instead of "unexpectedly failed" (rhbz#1090093)
- cpu: Add support for MPX and AVX512 Intel features (rhbz#1076170)

* Thu Jul  2 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-1
- Rebased to libvirt-1.2.17 (rhbz#1194593)
- The rebase also fixes the following bugs:
    rhbz#890648, rhbz#985653, rhbz#1021480, rhbz#1089914, rhbz#1131755
    rhbz#1171933, rhbz#1179680, rhbz#1181087, rhbz#1182388, rhbz#1186797
    rhbz#1186969, rhbz#1194593, rhbz#1196644, rhbz#1200206, rhbz#1201143
    rhbz#1201760, rhbz#1202208, rhbz#1207692, rhbz#1210352, rhbz#1220213
    rhbz#1223177, rhbz#1224053, rhbz#1224088, rhbz#1224233, rhbz#1224587
    rhbz#1225694, rhbz#1226234, rhbz#1226854, rhbz#1227180, rhbz#1227551
    rhbz#1227555, rhbz#1227558, rhbz#1227664, rhbz#1228007, rhbz#1229199
    rhbz#1229592, rhbz#1229666, rhbz#1230039, rhbz#1230137, rhbz#1230664
    rhbz#1232606, rhbz#1232880, rhbz#1234686, rhbz#1234729, rhbz#1235116
    rhbz#1236438, rhbz#1236496, rhbz#1236507, rhbz#1236585, rhbz#1236924
    rhbz#1238153, rhbz#1238338

* Thu Jun  4 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.16-1
- Rebased to libvirt-1.2.16 (rhbz#1194593)
- The rebase also fixes the following bugs:
    rhbz#847198, rhbz#890648, rhbz#893738, rhbz#976387, rhbz#981546
    rhbz#998813, rhbz#1066375, rhbz#1073233, rhbz#1073305, rhbz#1076354
    rhbz#1131486, rhbz#1143837, rhbz#1146539, rhbz#1159171, rhbz#1159219
    rhbz#1161541, rhbz#1164966, rhbz#1171984, rhbz#1174177, rhbz#1174226
    rhbz#1176020, rhbz#1176739, rhbz#1177599, rhbz#1181074, rhbz#1183893
    rhbz#1191227, rhbz#1194593, rhbz#1195882, rhbz#1197580, rhbz#1204006
    rhbz#1204033, rhbz#1206521, rhbz#1207043, rhbz#1211938, rhbz#1213345
    rhbz#1218145, rhbz#1218577, rhbz#1220195, rhbz#1220265, rhbz#1220474
    rhbz#1220702, rhbz#1220809, rhbz#1221047, rhbz#1221504, rhbz#1223631
    rhbz#1223688, rhbz#1224018, rhbz#1226849

* Mon May 11 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.15-2
- RHEL: Relax qemu-kvm dependency from libvirt-daemon-kvm (rhbz#1212642)
- caps: Fix regression defaulting to host arch (rhbz#1219191)

* Mon May  4 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.15-1
- Rebased to libvirt-1.2.15 (rhbz#1194593)
- The rebase also fixes the following bugs:
    rhbz#858147, rhbz#890606, rhbz#1043436, rhbz#1073305, rhbz#1076708
    rhbz#1084876, rhbz#1147847, rhbz#1161617, rhbz#1165119, rhbz#1168530
    rhbz#1171933, rhbz#1177062, rhbz#1177733, rhbz#1181465, rhbz#1192318
    rhbz#1200634, rhbz#1202606, rhbz#1202704, rhbz#1203628, rhbz#1203931
    rhbz#1206114, rhbz#1206479, rhbz#1206521, rhbz#1206625, rhbz#1207257
    rhbz#1208009, rhbz#1208176, rhbz#1208434, rhbz#1208763, rhbz#1209312
    rhbz#1209394, rhbz#1209813, rhbz#1210159, rhbz#1210545, rhbz#1210650
    rhbz#1210669, rhbz#1211436, rhbz#1211548, rhbz#1211550, rhbz#1213434
    rhbz#1213698, rhbz#1215569, rhbz#1216046

* Thu Apr  2 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.14-1
- Rebased to libvirt-1.2.14 (rhbz#1194593)
- The rebase also fixes the following bugs:
    rhbz#790583, rhbz#853839, rhbz#872424, rhbz#921426, rhbz#952499
    rhbz#958510, rhbz#1070695, rhbz#1125755, rhbz#1127045, rhbz#1129198
    rhbz#1135491, rhbz#1140958, rhbz#1141119, rhbz#1142631, rhbz#1142636
    rhbz#1143832, rhbz#1155887, rhbz#1161461, rhbz#1163553, rhbz#1164053
    rhbz#1166024, rhbz#1171484, rhbz#1173468, rhbz#1174147, rhbz#1176050
    rhbz#1177219, rhbz#1177237, rhbz#1179533, rhbz#1181062, rhbz#1187012
    rhbz#1187533, rhbz#1190590, rhbz#1196185, rhbz#1196644, rhbz#1196934
    rhbz#1197600, rhbz#1199036, rhbz#1199182, rhbz#1206365, rhbz#1206406
    rhbz#1206987, rhbz#1207122, rhbz#1207937
- RHEL: Hack around changed Broadwell/Haswell CPUs (rhbz#1199446)

* Thu Mar 26 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.13-1
- Rebased to libvirt-1.2.13 (rhbz#1194593)
- The rebase also fixes the following bugs:
    rhbz#872028, rhbz#907779, rhbz#927252, rhbz#956891, rhbz#1073506
    rhbz#1079917, rhbz#1095637, rhbz#1123767, rhbz#1125764, rhbz#1126762
    rhbz#1130390, rhbz#1131919, rhbz#1132900, rhbz#1135442, rhbz#1138125
    rhbz#1138516, rhbz#1138539, rhbz#1140034, rhbz#1140960, rhbz#1141159
    rhbz#1143921, rhbz#1146334, rhbz#1147195, rhbz#1151942, rhbz#1152404
    rhbz#1152473, rhbz#1153891, rhbz#1155843, rhbz#1158034, rhbz#1158722
    rhbz#1159180, rhbz#1160559, rhbz#1160995, rhbz#1161831, rhbz#1164627
    rhbz#1165485, rhbz#1165993, rhbz#1168849, rhbz#1169183, rhbz#1170092
    rhbz#1170140, rhbz#1170492, rhbz#1171533, rhbz#1171582, rhbz#1172015
    rhbz#1172468, rhbz#1172526, rhbz#1173420, rhbz#1174096, rhbz#1174154
    rhbz#1174569, rhbz#1175123, rhbz#1175449, rhbz#1176503, rhbz#1176510
    rhbz#1177723, rhbz#1178652, rhbz#1178850, rhbz#1178853, rhbz#1178986
    rhbz#1179678, rhbz#1179684, rhbz#1179981, rhbz#1181182, rhbz#1182467
    rhbz#1183869, rhbz#1183890, rhbz#1185165, rhbz#1186175, rhbz#1186199
    rhbz#1186765, rhbz#1186886, rhbz#1188914, rhbz#1189007, rhbz#1190956
    rhbz#1191016, rhbz#1191227, rhbz#1191355, rhbz#1191567, rhbz#1195461
    rhbz#1196503, rhbz#1196528, rhbz#1204017

* Wed Jan 28 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-16
- qemu: don't setup cpuset.mems if memory mode in numatune is not 'strict' (rhbz#1186094)
- lxc: don't setup cpuset.mems if memory mode in numatune is not 'strict' (rhbz#1186094)

* Wed Jan 21 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-15
- qemu: Add missing goto error in qemuRestoreCgroupState (rhbz#1161540)

* Wed Jan 21 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-14
- virNetworkDefUpdateIPDHCPHost: Don't crash when updating network (rhbz#1182486)
- Format CPU features even for host-model (rhbz#1182448)
- util: Add function virCgroupHasEmptyTasks (rhbz#1161540)
- util: Add virNumaGetHostNodeset (rhbz#1161540)
- qemu: Remove unnecessary qemuSetupCgroupPostInit function (rhbz#1161540)
- qemu: Save numad advice into qemuDomainObjPrivate (rhbz#1161540)
- qemu: Leave cpuset.mems in parent cgroup alone (rhbz#1161540)
- qemu: Fix hotplugging cpus with strict memory pinning (rhbz#1161540)
- util: Fix possible NULL dereference (rhbz#1161540)
- qemu_driver: fix setting vcpus for offline domain (rhbz#1161540)
- qemu: migration: Unlock vm on failed ACL check in protocol v2 APIs (CVE-2014-8136)
- CVE-2015-0236: qemu: Check ACLs when dumping security info from save image (CVE-2015-0236)
- CVE-2015-0236: qemu: Check ACLs when dumping security info from snapshots (CVE-2015-0236)
- Check for domain liveness in qemuDomainObjExitMonitor (rhbz#1161024)
- Mark the domain as active in qemuhotplugtest (rhbz#1161024)
- Fix vmdef usage while in monitor in qemuDomainHotplugVcpus (rhbz#1161024)
- Fix vmdef usage while in monitor in BlockStat* APIs (rhbz#1161024)
- Fix vmdef usage while in monitor in qemu process (rhbz#1161024)
- Fix vmdef usage after domain crash in monitor on device detach (rhbz#1161024)
- Fix vmdef usage after domain crash in monitor on device attach (rhbz#1161024)

* Wed Jan 14 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-13
- conf: Fix memory leak when parsing invalid network XML (rhbz#1180136)
- qxl: change the default value for vgamem_mb to 16 MiB (rhbz#1181052)
- qemuxml2argvtest: Fix test after change of qxl vgamem_mb default (rhbz#1181052)
- conf: fix crash when hotplug a channel chr device with no target (rhbz#1181408)
- qemu: forbid second blockcommit during active commit (rhbz#1135339)
- qemu_monitor: introduce new function to get QOM path (rhbz#1180574)
- qemu_process: detect updated video ram size values from QEMU (rhbz#1180574)

* Wed Jan  7 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-12
- Fix hotplugging of block device-backed usb disks (rhbz#1175668)
- qemu: Create memory-backend-{ram, file} iff needed (rhbz#1175397)
- conf: Don't format actual network definition in migratable XML (rhbz#1177194)

* Wed Dec 17 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-11
- virsh: vol-upload disallow negative offset (rhbz#1087104)
- storage: fix crash caused by no check return before set close (rhbz#1087104)
- qemu: Fix virsh freeze when blockcopy storage file is removed (rhbz#1139567)
- security: Manage SELinux labels on shared/readonly hostdev's (rhbz#1082521)
- nwfilter: fix crash when adding non-existing nwfilter (rhbz#1169409)
- conf: Fix libvirtd crash matching hostdev XML (rhbz#1174053)
- qemu: Resolve Coverity REVERSE_INULL (rhbz#1172570)
- CVE-2014-8131: Fix possible deadlock and segfault in qemuConnectGetAllDomainStats() (CVE-2014-8131)
- qemu: bulk stats: Fix logic in monitor handling (rhbz#1172570)
- qemu: avoid rare race when undefining domain (rhbz#1150505)
- Do not format CPU features without a model (rhbz#1151885)
- Ignore CPU features without a model for host-passthrough (rhbz#1151885)
- Silently ignore MAC in NetworkLoadConfig (rhbz#1156367)
- Generate a MAC when loading a config instead of package update (rhbz#1156367)
- qemu: move setting emulatorpin ahead of monitor showing up (rhbz#1170484)
- util: Introduce flags field for macvtap creation (rhbz#1081461)
- network: Bring netdevs online later (rhbz#1081461)
- qemu: always call qemuInterfaceStartDevices() when starting CPUs (rhbz#1081461)
- qemu: add a qemuInterfaceStopDevices(), called when guest CPUs stop (rhbz#1081461)
- conf: replace call to virNetworkFree() with virObjectUnref() (rhbz#1099210)
- util: new functions for setting bridge and bridge port attributes (rhbz#1099210)
- util: functions to manage bridge fdb (forwarding database) (rhbz#1099210)
- conf: new network bridge device attribute macTableManager (rhbz#1099210)
- network: save bridge name in ActualNetDef when actualType==network too (rhbz#1099210)
- network: store network macTableManager setting in NetDef actual object (rhbz#1099210)
- network: setup bridge devices for macTableManager='libvirt' (rhbz#1099210)
- qemu: setup tap devices for macTableManager='libvirt' (rhbz#1099210)
- qemu: add/remove bridge fdb entries as guest CPUs are started/stopped (rhbz#1099210)
- virsh: document block.n.allocation stat (rhbz#1041569)
- getstats: avoid memory leak on OOM (rhbz#1041569)
- getstats: improve documentation (rhbz#1041569)
- getstats: start giving offline block stats (rhbz#1041569)
- getstats: add block.n.path stat (rhbz#1041569)
- qemuMonitorJSONBlockStatsUpdateCapacity: Don't skip disks (rhbz#1041569)
- getstats: prepare monitor collection for recursion (rhbz#1041569)
- getstats: perform recursion in monitor collection (rhbz#1041569)
- getstats: prepare for dynamic block.count stat (rhbz#1041569)
- getstats: add new flag for block backing chain (rhbz#1041569)
- getstats: split block stats reporting for easier recursion (rhbz#1041569)
- getstats: crawl backing chain for qemu (rhbz#1041569)
- logical: Add "--type snapshot" to lvcreate command (rhbz#1166592)

* Mon Dec  1 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-10
- qemu: add the missing jobinfo type in qemuDomainGetJobInfo (rhbz#1167883)
- network: Fix upgrade from libvirt older than 1.2.4 (rhbz#1167145)
- qemu: fix domain startup failing with 'strict' mode in numatune (rhbz#1168866)
- qemu: Don't track quiesced state of FSs (rhbz#1160084)
- qemu: fix block{commit,copy} abort handling (rhbz#1135169)

* Tue Nov 25 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-9
- doc: fix mismatched ACL attribute name (rhbz#1161358)
- qemu: monitor: Rename and improve qemuMonitorGetPtyPaths (rhbz#1146944)
- conf: Add channel state for virtio channels to the XML (rhbz#1146944)
- qemu: Add handling for VSERPORT_CHANGE event (rhbz#1146944)
- qemu: chardev: Extract more information about character devices (rhbz#1146944)
- qemu: process: Refresh virtio channel guest state when connecting to mon (rhbz#1146944)
- event: Add guest agent lifecycle event (rhbz#1146944)
- examples: Add support for the guest agent lifecycle event (rhbz#1146944)
- qemu: Emit the guest agent lifecycle event (rhbz#1146944)
- internal: add macro to round value to the next closest power of 2 (rhbz#1076098)
- video: cleanup usage of vram attribute and update documentation (rhbz#1076098)
- QXL: fix setting ram and vram values for QEMU QXL device (rhbz#1076098)
- caps: introduce new QEMU capability for vgamem_mb device property (rhbz#1076098)
- qemu-command: use vram attribute for all video devices (rhbz#1076098)
- qemu-command: introduce new vgamem attribute for QXL video device (rhbz#1076098)

* Fri Nov 21 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-8
- qemu: Fix crash in tunnelled migration (rhbz#1147331)
- qemu: Really fix crash in tunnelled migration (rhbz#1147331)
- qemu: Update fsfreeze status on domain state transitions (rhbz#1160084)
- qemuPrepareNVRAM: Save domain conf only if domain's persistent (rhbz#1026772)
- docs: Document NVRAM behavior on transient domains (rhbz#1026772)
- Fix build in qemu_capabilities (rhbz#1165782)
- qemu: Support OVMF on armv7l aarch64 guests (rhbz#1165782)
- qemu: Drop OVMF whitelist (rhbz#1165782)
- storage: Fix issue finding LU's when block doesn't exist (rhbz#1152382)
- storage: Add thread to refresh for createVport (rhbz#1152382)
- storage: qemu: Fix security labelling of new image chain elements (rhbz#1151718)
- virsh: sync domdisplay help and manual (rhbz#997802)
- docs: domain: Move docs for storage hosts under the <source> element (rhbz#1164528)
- test: virstoragetest: Add testing of network disk details (rhbz#1164528)
- util: storage: Copy hosts of a storage file only if they exist (rhbz#1164528)
- qemu: Refactor qemuBuildNetworkDriveURI to take a virStorageSourcePtr (rhbz#1164528)
- tests: Reflow the expected output from RBD disk test (rhbz#1164528)
- util: split out qemuParseRBDString into a common helper (rhbz#1164528)
- util: storagefile: Split out parsing of NBD string into a separate func (rhbz#1164528)
- storage: Allow parsing of RBD backing strings when building backing chain (rhbz#1164528)
- storage: rbd: qemu: Add support for specifying internal RBD snapshots (rhbz#1164528)
- storage: rbd: Implement support for passing config file option (rhbz#1164528)

* Fri Nov 14 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-7
- qemu: avoid rare race when undefining domain (rhbz#1150505)
- qemu: stop NBD server after successful migration (rhbz#1160212)
- Require at least one console for LXC domain (rhbz#1155410)
- remote: Fix memory leak in remoteConnectGetAllDomainStats (rhbz#1158715)
- CVE-2014-7823: dumpxml: security hole with migratable flag (CVE-2014-7823)
- Free job statistics from the migration cookie (rhbz#1161124)
- Fix virDomainChrEquals for spicevmc (rhbz#1162097)
- network: fix call virNetworkEventLifecycleNew when networkStartNetwork fail (rhbz#1162915)
- Do not crash on gluster snapshots with no host name (rhbz#1162974)
- nwfilter: fix deadlock caused updating network device and nwfilter (rhbz#1143780)
- util: eliminate "use after free" in callers of virNetDevLinkDump (rhbz#1163463)
- storage: Check for valid fc_host parent at startup (rhbz#1160565)
- storage: Ensure fc_host parent matches wwnn/wwpn (rhbz#1160565)
- storage: Don't use a stack copy of the adapter (rhbz#1160926)
- storage: Introduce virStoragePoolSaveConfig (rhbz#1160926)
- storage: Introduce 'managed' for the fchost parent (rhbz#1160926)
- qemu: Always set migration capabilities (rhbz#1163953)

* Tue Nov  4 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-6
- qemu: support nospace reason in io error event (rhbz#1119784)
- RHEL: Add support for QMP I/O error reason (rhbz#1119784)
- nodeinfo: fix nodeGetFreePages when max node is zero (rhbz#1145048)
- nodeGetFreePages: Push forgotten change (rhbz#1145048)
- conf: tests: fix virDomainNetDefFormat for vhost-user in client mode (rhbz#1155458)
- util: string: Add helper to check whether string is empty (rhbz#1142693)
- qemu: restore: Fix restoring of VM when the restore hook returns empty XML (rhbz#1142693)
- security_selinux: Don't relabel /dev/net/tun (rhbz#1095636)
- qemu: Fix updating bandwidth limits in live XML (rhbz#1146511)
- qemu: save domain status after set the blkio parameters (rhbz#1146511)
- qemu: call qemuDomainObjBeginJob/qemuDomainObjEndJob in qemuDomainSetInterfaceParameters (rhbz#1146511)
- qemu: save domain status after set domain's numa parameters (rhbz#1146511)
- qemu: forbid snapshot-delete --children-only on external snapshot (rhbz#956506)
- qemu: better error message when block job can't succeed (rhbz#1140981)
- Reject live update of offloading options (rhbz#1155441)
- virutil: Introduce virGetSCSIHostNumber (rhbz#1146837)
- virutil: Introduce virGetSCSIHostNameByParentaddr (rhbz#1146837)
- storage_conf: Resolve libvirtd crash matching scsi_host (rhbz#1146837)
- Match scsi_host pools by parent address first (rhbz#1146837)
- Relax duplicate SCSI host pool checking (rhbz#1146837)
- qemu: Remove possible NULL deref in debug output (rhbz#1141621)
- virsh: Adjust the text in man page regarding qemu-attach (rhbz#1141621)
- hotplug: Check for alias in controller detach (rhbz#1141621)
- hotplug: Check for alias in disk detach (rhbz#1141621)
- hotplug: Check for alias in hostdev detach (rhbz#1141621)
- hotplug: Check for alias in chrdev detach (rhbz#1141621)
- hotplug: Check for alias in net detach (rhbz#1141621)
- qemu-attach: Assign device aliases (rhbz#1141621)
- hotplug: fix char device detach (rhbz#1141621)
- storage: Fix crash when parsing backing store URI with schema (rhbz#1156288)
- remote: fix jump depends on uninitialised value (rhbz#1158715)
- qemu: Release nbd port from migrationPorts instead of remotePorts (rhbz#1159245)
- conf: add trustGuestRxFilters attribute to network and domain interface (rhbz#848199)
- network: set interface actual trustGuestRxFilters from network/portgroup (rhbz#848199)
- util: define virNetDevRxFilter and basic utility functions (rhbz#848199)
- qemu: qemuMonitorQueryRxFilter - retrieve guest netdev rx-filter (rhbz#848199)
- qemu: add short document on qemu event handlers (rhbz#848199)
- qemu: setup infrastructure to handle NIC_RX_FILTER_CHANGED event (rhbz#848199)
- qemu: change macvtap device MAC address in response to NIC_RX_FILTER_CHANGED (rhbz#848199)
- util: Functions to update host network device's multicast filter (rhbz#848199)
- qemu: change macvtap multicast list in response to NIC_RX_FILTER_CHANGED (rhbz#848199)
- virnetdev: Resolve Coverity DEADCODE (rhbz#848199)
- virnetdev: Resolve Coverity FORWARD_NULL (rhbz#848199)
- virnetdev: Resolve Coverity RESOURCE_LEAK (rhbz#848199)
- lxc: improve error message for invalid blkiotune settings (rhbz#1131306)
- qemu: improve error message for invalid blkiotune settings (rhbz#1131306)
- Do not probe for power mgmt capabilities in lxc emulator (rhbz#1159227)
- qemu: make advice from numad available when building commandline (rhbz#1138545)

* Thu Oct  9 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-5
- qemuPrepareNVRAM: Save domain after NVRAM path generation (rhbz#1026772)
- Fix crash cpu_shares change event crash on domain startup (rhbz#1147494)
- Don't verify CPU features with host-passthrough (rhbz#1147584)
- Also filter out non-migratable features out of host-passthrough (rhbz#1147584)
- selinux: Avoid label reservations for type = none (rhbz#1138487)
- qemu: bulk stats: extend internal collection API (rhbz#1113116)
- qemu: bulk stats: implement CPU stats group (rhbz#1113116)
- qemu: bulk stats: implement balloon group (rhbz#1113116)
- qemu: bulk stats: implement VCPU group (rhbz#1113116)
- qemu: bulk stats: implement interface group (rhbz#1113116)
- qemu: bulk stats: implement block group (rhbz#1113116)
- virsh: add options to query bulk stats group (rhbz#1113116)
- lib: De-duplicate stats group documentation for all stats functions (rhbz#1113116)
- lib: Document that virConnectGetAllDomainStats may omit some stats fields (rhbz#1113116)
- man: virsh: Add docs for supported stats groups (rhbz#1113116)
- qemu: monitor: return block stats data as a hash to avoid disk mixup (rhbz#1113116)
- qemu: monitor: Avoid shadowing variable "devname" on FreeBSD (rhbz#1113116)
- qemu: monitor: Add helper function to fill physical/virtual image size (rhbz#1113116)
- qemu: bulk stats: add block allocation information (rhbz#1113116)
- qemu: json: Fix missing break in error reporting function (rhbz#1113116)
- qemu: monitor: Avoid shadowing variable "devname" on FreeBSD. Again. (rhbz#1113116)
- docs, conf, schema: add support for shmem device (rhbz#1126991)
- qemu: add capability probing for ivshmem device (rhbz#1126991)
- qemu: Build command line for ivshmem device (rhbz#1126991)
- minor shmem clean-ups (rhbz#1126991)
- virSecuritySELinuxSetTapFDLabel: Temporarily revert to old behavior (rhbz#1095636)
- domain_conf: fix domain deadlock (CVE-2014-3657)
- qemu: support relative backing for RHEL 7.0.z qemu (rhbz#1150322)
- qemu: Fix hot unplug of SCSI_HOST device (rhbz#1141732)
- qemu: Remove need for virConnectPtr in hotunplug detach host, net (rhbz#1141732)

* Fri Sep 26 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-4
- Fix libvirtd crash when removing metadata (rhbz#1143955)
- Fix leak in x86UpdateHostModel (rhbz#1144303)
- Move the FIPS detection from capabilities (rhbz#1135431)
- qemu: raise an error when trying to use readonly sata disks (rhbz#1112939)
- virsh-host: fix pagesize unit of freepages (rhbz#1145048)
- nodeinfo: report error when given node is out of range (rhbz#1145050)
- Fix typo of virNodeGetFreePages comment (rhbz#1145050)
- nodeinfo: Prefer MIN in nodeGetFreePages (rhbz#1145050)
- Fix bug with loading bridge name for active domain during libvirtd start (rhbz#1140085)
- qemu: save image: Split out user provided XML checker (rhbz#1142693)
- qemu: save image: Add possibility to return XML stored in the image (rhbz#1142693)
- qemu: save image: Split out new definition check/update (rhbz#1142693)
- qemu: save image: Split out checks done only when editing the save img (rhbz#1142693)
- qemu: hook: Provide hook when restoring a domain save image (rhbz#1142693)
- qemu: Expose additional migration statistics (rhbz#1013055)
- qemu: Fix old tcp:host URIs more cleanly (rhbz#1013055)
- qemu: Prepare support for arbitrary migration protocol (rhbz#1013055)
- qemu: Add RDMA migration capabilities (rhbz#1013055)
- qemu: RDMA migration support (rhbz#1013055)
- qemu: Memory pre-pinning support for RDMA migration (rhbz#1013055)
- qemu: Fix memory leak in RDMA migration code (rhbz#1013055)
- schemas: finish virTristate{Bool, Switch} transition (rhbz#1139364)
- conf: split out virtio net driver formatting (rhbz#1139364)
- conf: remove redundant local variable (rhbz#1139364)
- conf: add options for disabling segment offloading (rhbz#1139364)
- qemu: wire up virtio-net segment offloading options (rhbz#1139364)
- spec: Enable qemu driver for RHEL-7 on aarch64 (rhbz#1142448)
- blkdeviotune: fix bug with saving values into live XML (rhbz#1146511)
- security: Fix labelling host devices (rhbz#1146550)
- qemu: Add missing goto on rawio (rhbz#1103739)
- hostdev: Add "rawio" attribute to _virDomainHostdevSubsysSCSI (rhbz#1103739)
- qemu: Process the hostdev "rawio" setting (rhbz#1103739)
- util: Add function to check if a virStorageSource is "empty" (rhbz#1138231)
- util: storage: Allow metadata crawler to report useful errors (rhbz#1138231)
- qemu: Sanitize argument names and empty disk check in qemuDomainDetermineDiskChain (rhbz#1138231)
- qemu: Report better errors from broken backing chains (rhbz#1138231)
- storage: Improve error message when traversing backing chains (rhbz#1138231)
- qemu: Always re-detect backing chain (rhbz#1144922)
- event: introduce new event for tunable values (rhbz#1115898)
- tunable_event: extend debug message and tweak limit for remote message (rhbz#1115898)
- add an example how to use tunable event (rhbz#1115898)
- Fix MinGW build (rhbz#1115898)
- event_example: cleanup example code for tunable event (rhbz#1115898)
- cputune_event: queue the event for cputune updates (rhbz#1115898)
- blkdeviotune: trigger tunable event for blkdeviotune updates (rhbz#1115898)
- Rename tunable event constants (rhbz#1115898)
- Fix typo s/EMULATORIN/EMULATORPIN/ (rhbz#1115898)
- Check for NULL in qemu monitor event filter (rhbz#1144920)

* Thu Sep 18 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-3
- virsh: Move --completed from resume to domjobinfo (rhbz#1063724)
- qemu_driver: Resolve Coverity COPY_PASTE_ERROR (rhbz#1141209)
- virfile: Resolve Coverity DEADCODE (rhbz#1141209)
- lxc: Resolve Coverity FORWARD_NULL (rhbz#1141209)
- qemu: Resolve Coverity FORWARD_NULL (rhbz#1141209)
- qemu: Resolve Coverity FORWARD_NULL (rhbz#1141209)
- xen: Resolve Coverity NEGATIVE_RETURNS (rhbz#1141209)
- qemu: Resolve Coverity NEGATIVE_RETURNS (rhbz#1141209)
- qemu: Resolve Coverity NEGATIVE_RETURNS (rhbz#1141209)
- virsh: Resolve Coverity NEGATIVE_RETURNS (rhbz#1141209)
- daemon: Resolve Coverity RESOURCE_LEAK (rhbz#1141209)
- domain_conf: Resolve Coverity COPY_PASTE_ERROR (rhbz#1141209)
- storage_conf: Fix libvirtd crash when defining scsi storage pool (rhbz#1141943)
- qemu: time: Report errors if agent command fails (rhbz#1142294)
- util: storage: Copy driver type when initializing chain element (rhbz#1140984)
- docs, conf, schema: add support for shared memory mapping (rhbz#1133144)
- qemu: add support for shared memory mapping (rhbz#1133144)
- rpc: reformat the flow to make a bit more sense (rhbz#927369)
- remove redundant pidfile path constructions (rhbz#927369)
- util: fix potential leak in error codepath (rhbz#927369)
- util: get rid of unnecessary umask() call (rhbz#927369)
- rpc: make daemon spawning a bit more intelligent (rhbz#927369)
- conf: add backend element to interfaces (rhbz#1139362)
- Wire up the interface backend options (rhbz#1139362)
- CVE-2014-3633: qemu: blkiotune: Use correct definition when looking up disk (CVE-2014-3633)
- qemu: fix crash with shared disks (rhbz#1142722)
- nvram: Fix permissions (rhbz#1026772)
- libvirt.spec: Fix permission even for libvirt-driver-qemu (rhbz#1026772)
- virDomainUndefineFlags: Allow NVRAM unlinking (rhbz#1026772)
- formatdomain: Update <loader/> example to match the rest (rhbz#1026772)
- domaincaps: Expose UEFI capability (rhbz#1026772)
- qemu_capabilities: Change virQEMUCapsFillDomainCaps signature (rhbz#1026772)
- domaincaps: Expose UEFI binary path, if it exists (rhbz#1026772)
- domaincapstest: Run cleanly on systems missing OVMF firmware (rhbz#1026772)
- conf: Disallow nonexistent NUMA nodes for hugepages (rhbz#1135396)
- qemu: Honor hugepages for UMA domains (rhbz#1135396)
- RHEL: Fix maxvcpus output (rhbz#1092363)
- virsh: Add iothread to 'attach-disk' (rhbz#1101574)
- qemu: Issue query-iothreads and to get list of active IOThreads (rhbz#1101574)
- vircgroup: Introduce virCgroupNewIOThread (rhbz#1101574)
- qemu_domain: Add niothreadpids and iothreadpids (rhbz#1101574)
- qemu_cgroup: Introduce cgroup functions for IOThreads (rhbz#1101574)
- qemu: Allow pinning specific IOThreads to a CPU (rhbz#1101574)
- domain_conf: Add iothreadpin to cputune (rhbz#1101574)
- vircgroup: Fix broken builds without cgroups (rhbz#1101574)
- cputune: allow interleaved xml (rhbz#1101574)
- qemu: Fix iothreads issue (rhbz#1101574)
- qemu_cgroup: Adjust spacing around incrementor (rhbz#1101574)
- qemu: Fix call in qemuDomainSetNumaParamsLive for virCgroupNewIOThread (rhbz#1101574)
- qemu: Need to check for capability before query (rhbz#1101574)
- qemu: Don't fail startup/attach for IOThreads if no JSON (rhbz#1101574)
- Fixes for domains with no iothreads (rhbz#1101574)

* Wed Sep 10 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-2
- remote: Fix memory leak on error path when deserializing bulk stats (rhbz#1136350)
- spec: Fix preun script for daemon (rhbz#1136736)
- security: fix DH key generation when FIPS mode is on (rhbz#1128497)
- tests: force FIPS testing mode with new enough GNU TLS versions (rhbz#1128497)
- Don't include non-migratable features in host-model (rhbz#1138221)
- qemu: Rename DEFAULT_JOB_MASK to QEMU_DEFAULT_JOB_MASK (rhbz#1134154)
- qemu: snapshot: Fix job handling when creating snapshots (rhbz#1134154)
- qemu: snapshot: Acquire job earlier on snapshot revert/delete (rhbz#1134154)
- qemu: snapshot: Fix snapshot function header formatting and spacing (rhbz#1134154)
- qemu: snapshot: Simplify error paths (rhbz#1134154)
- qemu: Propagate QEMU errors during incoming migrations (rhbz#1090093)
- Refactor job statistics (rhbz#1063724)
- qemu: Avoid incrementing jobs_queued if virTimeMillisNow fails (rhbz#1063724)
- Add support for fetching statistics of completed jobs (rhbz#1063724)
- qemu: Silence coverity on optional migration stats (rhbz#1063724)
- virsh: Add support for completed job stats (rhbz#1063724)
- qemu: Transfer migration statistics to destination (rhbz#1063724)
- qemu: Recompute downtime and total time when migration completes (rhbz#1063724)
- qemu: Transfer recomputed stats back to source (rhbz#1063724)
- conf: Extend <loader/> and introduce <nvram/> (rhbz#1112257)
- qemu: Implement extended loader and nvram (rhbz#1112257)
- qemu: Automatically create NVRAM store (rhbz#1112257)

* Tue Sep  2 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-1
- Rebased to libvirt-1.2.8 (rhbz#1035158)
- The rebase also fixes the following bugs:
    rhbz#927369, rhbz#957293, rhbz#999926, rhbz#1021703, rhbz#1043735
    rhbz#1047818, rhbz#1062142, rhbz#1064770, rhbz#1072653, rhbz#1078126
    rhbz#1095636, rhbz#1103245, rhbz#1119215, rhbz#1121837, rhbz#1121955
    rhbz#1122455, rhbz#1126329, rhbz#1126721, rhbz#1126909, rhbz#1128097
    rhbz#1128751, rhbz#1129207, rhbz#1129372, rhbz#1129998, rhbz#1130089
    rhbz#1130379, rhbz#1131306, rhbz#1131445, rhbz#1131788, rhbz#1131811
    rhbz#1131819, rhbz#1131876, rhbz#1132301, rhbz#1132305, rhbz#1132347

* Mon Aug  4 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.7-1
- Rebased to libvirt-1.2.7 (rhbz#1035158)
- The rebase also fixes the following bugs:
    rhbz#823535, rhbz#872628, rhbz#874418, rhbz#878394, rhbz#880483
    rhbz#921094, rhbz#963817, rhbz#964177, rhbz#967493, rhbz#967494
    rhbz#972964, rhbz#983350, rhbz#985782, rhbz#985980, rhbz#990319
    rhbz#990418, rhbz#991290, rhbz#992980, rhbz#994731, rhbz#995377
    rhbz#997627, rhbz#997802, rhbz#1006700, rhbz#1007698, rhbz#1007759
    rhbz#1010885, rhbz#1022874, rhbz#1023366, rhbz#1025407, rhbz#1027076
    rhbz#1029266, rhbz#1029732, rhbz#1032363, rhbz#1033020, rhbz#1033398
    rhbz#1033704, rhbz#1035128, rhbz#1046192, rhbz#1049038, rhbz#1052114
    rhbz#1056902, rhbz#1062142, rhbz#1063837, rhbz#1066280, rhbz#1066894
    rhbz#1067338, rhbz#1069552, rhbz#1069784, rhbz#1070680, rhbz#1072141
    rhbz#1072677, rhbz#1073368, rhbz#1073506, rhbz#1074086, rhbz#1075290
    rhbz#1075299, rhbz#1076957, rhbz#1076959, rhbz#1076960, rhbz#1076962
    rhbz#1077009, rhbz#1077572, rhbz#1078590, rhbz#1079162, rhbz#1079173
    rhbz#1080859, rhbz#1081881, rhbz#1081932, rhbz#1082124, rhbz#1083345
    rhbz#1084360, rhbz#1085706, rhbz#1085769, rhbz#1086121, rhbz#1086331
    rhbz#1086704, rhbz#1087104, rhbz#1087671, rhbz#1088293, rhbz#1088667
    rhbz#1088787, rhbz#1088864, rhbz#1089179, rhbz#1089378, rhbz#1091132
    rhbz#1091866, rhbz#1092038, rhbz#1092253, rhbz#1093127, rhbz#1095035
    rhbz#1097028, rhbz#1097503, rhbz#1097677, rhbz#1097968, rhbz#1098659
    rhbz#1099978, rhbz#1100086, rhbz#1100769, rhbz#1101059, rhbz#1101510
    rhbz#1101987, rhbz#1101999, rhbz#1102426, rhbz#1102457, rhbz#1102611
    rhbz#1104992, rhbz#1104993, rhbz#1105939, rhbz#1108593, rhbz#1110198
    rhbz#1110212, rhbz#1110673, rhbz#1111044, rhbz#1112939, rhbz#1113332
    rhbz#1113668, rhbz#1113751, rhbz#1113868, rhbz#1118710, rhbz#1119206
    rhbz#1119387, rhbz#1119592, rhbz#1120474, rhbz#1122255, rhbz#1122973
- spec: Enable qemu driver for RHEL-7 on ppc64 (rhbz#1120474)

* Fri Aug  1 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.6-1
- Rebased to libvirt-1.2.6 (rhbz#1035158)

* Mon Mar 24 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-29
- nwfilter: Increase buffer size for libpcap (rhbz#1078347)
- nwfilter: Display pcap's error message when pcap setup fails (rhbz#1078347)
- nwfilter: Fix double free of pointer (rhbz#1071181)

* Tue Mar 18 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-28
- qemu: Forbid "sgio" support for SCSI generic host device (rhbz#957292)
- qemu: monitor: Fix invalid parentheses (rhbz#1075973)
- qemu: Introduce qemuDomainDefCheckABIStability (rhbz#1076503)

* Wed Mar 12 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-27
- spec: Let translations be properly updated (rhbz#1030368)
- Update translation to supported languages (rhbz#1030368)
- Add a mutex to serialize updates to firewall (rhbz#1074003)

* Wed Mar  5 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-26
- virNetDevVethCreate: Serialize callers (rhbz#1014604)
- qemuBuildNicDevStr: Adapt to new advisory on multiqueue (rhbz#1071888)

* Wed Feb 26 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-25
- maint: fix comma style issues: conf (rhbz#1032370)
- Allow <source> for type=block to have no dev (rhbz#1032370)
- Allow LUN type disks to have no source (rhbz#1032370)
- virsh-volume: Unify strigification of volume type (rhbz#1032370)
- conf: Refactor virDomainDiskSourcePoolDefParse (rhbz#1032370)
- conf: Split out code to parse the source of a disk definition (rhbz#1032370)
- conf: Rename virDomainDiskHostDefFree to virDomainDiskHostDefClear (rhbz#1032370)
- conf: Refactor virDomainDiskSourceDefParse (rhbz#1032370)
- storage: fix RNG validation of gluster via netfs (rhbz#1032370)
- maint: fix comment typos. (rhbz#1032370)
- storage: use valid XML for awkward volume names (rhbz#1032370)
- build: Don't fail on '&lt; ' or '&gt; ' with old xmllint (rhbz#1032370)
- storage: allow interleave in volume XML (rhbz#1032370)
- storage: expose volume meta-type in XML (rhbz#1032370)
- storage: initial support for linking with libgfapi (rhbz#1032370)
- storage: document existing pools (rhbz#1032370)
- storage: document gluster pool (rhbz#1032370)
- storage: implement rudimentary glusterfs pool refresh (rhbz#1032370)
- storage: add network-dir as new storage volume type (rhbz#1032370)
- storage: improve directory support in gluster pool (rhbz#1032370)
- storage: improve allocation stats reported on gluster files (rhbz#1032370)
- storage: improve handling of symlinks in gluster (rhbz#1032370)
- storage: probe qcow2 volumes in gluster pool (rhbz#1032370)
- storage: fix typo in previous patch (rhbz#1032370)
- conf: Export virStorageVolType enum helper functions (rhbz#1032370)
- test: Implement fake storage pool driver in qemuxml2argv test (rhbz#1032370)
- storage: reduce number of stat calls (rhbz#1032370)
- storage: use simpler 'char *' (rhbz#1032370)
- storage: refactor backing chain division of labor (rhbz#1032370)
- storage: always probe type with buffer (rhbz#1032370)
- storage: don't read storage volumes in nonblock mode (rhbz#1032370)
- storage: skip selinux cleanup when fd not available (rhbz#1032370)
- storage: use correct type for array count (rhbz#1032370)
- storage: allow interleave in pool XML (rhbz#1032370)
- qemuxml2argv: Add test to verify correct usage of disk type="volume" (rhbz#1032370)
- qemuxml2argv: Add test for disk type='volume' with iSCSI pools (rhbz#1032370)
- tests: Fix comment for fake storage pool driver (rhbz#1032370)
- conf: Support disk source formatting without needing a virDomainDiskDefPtr (rhbz#1032370)
- conf: Clean up virDomainDiskSourceDefFormatInternal (rhbz#1032370)
- conf: Split out seclabel formating code for disk source (rhbz#1032370)
- conf: Export disk source formatter and parser (rhbz#1032370)
- snapshot: conf: Use common parsing and formatting functions for source (rhbz#1032370)
- snapshot: conf: Fix NULL dereference when <driver> element is empty (rhbz#1032370)
- conf: Add functions to copy and free network disk source definitions (rhbz#1032370)
- qemu: snapshot: Detect internal snapshots also for sheepdog and RBD (rhbz#1032370)
- conf: Add helper do clear disk source authentication struct (rhbz#1032370)
- qemu: snapshot: Touch up error message (rhbz#1032370)
- qemu: snapshot: Add functions similar to disk source pool translation (rhbz#1032370)
- qemu: Refactor qemuTranslateDiskSourcePool (rhbz#1032370)
- qemu: Split out formatting of network disk source URI (rhbz#1032370)
- qemu: Simplify call pattern of qemuBuildDriveURIString (rhbz#1032370)
- qemu: Use qemuBuildNetworkDriveURI to handle http/ftp and friends (rhbz#1032370)
- qemu: Migrate sheepdog source generation into common function (rhbz#1032370)
- qemu: Split out NBD command generation (rhbz#1032370)
- qemu: Unify formatting of RBD sources (rhbz#1032370)
- qemu: Refactor disk source string formatting (rhbz#1032370)
- qemu: Clear old translated pool source (rhbz#1032370)
- qemu: snapshots: Declare supported and unsupported snapshot configs (rhbz#1032370)
- domainsnapshotxml2xmltest: Clean up labels and use bool instead of int (rhbz#1032370)
- domainsnapshotxml2xmltest: Allow for better testing of snapshots (rhbz#1032370)
- domainsnapshotxml2xml: Move files with conflicting names (rhbz#1032370)
- domainsnapshotxml2xmltest: Add existing files as new tests (rhbz#1032370)
- domainsnapshotxml2xmltest: Add test case for empty driver element (rhbz#1032370)
- qemu: Fix indentation in qemuTranslateDiskSourcePool (rhbz#1032370)
- qemu: snapshot: Fix incorrect disk type for auto-generated disks (rhbz#1032370)
- storage: fix omitted slash in gluster volume URI (rhbz#1032370)
- virsh: domain: Fix undefine with storage of 'volume' disks (rhbz#1032370)
- snapshot: schema: Split out snapshot disk driver definition (rhbz#1032370)
- storage: Add gluster pool filter and fix virsh pool listing (rhbz#1032370)
- storage: fix bogus target in gluster volume xml (rhbz#1032370)
- storage: Improve error message when a storage backend is missing (rhbz#1032370)
- storage: Break long lines and clean up spaces in storage backend header (rhbz#1032370)
- storage: Support deletion of volumes on gluster pools (rhbz#1032370)
- qemu: snapshot: Avoid libvirtd crash when qemu crashes while snapshotting (rhbz#1032370)
- qemu: snapshot: Forbid snapshots when backing is a scsi passthrough disk (rhbz#1034993)
- qemu: Avoid crash in qemuDiskGetActualType (rhbz#1032370)
- snapshot: Add support for specifying snapshot disk backing type (rhbz#1032370)
- conf: Move qemuDiskGetActualType to virDomainDiskGetActualType (rhbz#1032370)
- conf: Move qemuSnapshotDiskGetActualType to virDomainSnapshotDiskGetActualType (rhbz#1032370)
- storage: Add file storage APIs in the default storage driver (rhbz#1032370)
- storage: add file functions for local and block files (rhbz#1032370)
- storage: Add storage file backends for gluster (rhbz#1032370)
- qemu: Switch snapshot deletion to the new API functions (rhbz#1032370)
- qemu: snapshot: Use new APIs to detect presence of existing storage files (rhbz#1032370)
- qemu: snapshot: Add support for external active snapshots on gluster (rhbz#1032370)
- storage: Fix build with older compilers afeter gluster snapshot series (rhbz#1032370)
- storage: gluster: Don't leak private data when storage file init fails (rhbz#1032370)
- spec: Use correct versions of libgfapi in RHEL builds (rhbz#1032370)
- spec: Fix braces around macros (rhbz#1032370)
- build: use --with-systemd-daemon as configure option (rhbz#1032695)
- spec: require device-mapper-devel for storage-disk (rhbz#1032695)
- spec: make systemd_daemon usage configurable (rhbz#1032695)

* Tue Feb 25 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-24
- Block info query: Add check for transient domain (rhbz#1065531)
- Fix minor typos in messages and docs (rhbz#1045643)
- LXC: Free variable vroot in lxcDomainDetachDeviceHostdevUSBLive() (rhbz#1045643)
- LXC: free dst before lxcDomainAttachDeviceDiskLive returns (rhbz#1045643)
- maint: fix comment typos (rhbz#1045643)
- storage: avoid short reads while chasing backing chain (rhbz#1045643)
- Don't block use of USB with containers (rhbz#1045643)
- Fix path used for USB device attach with LXC (rhbz#1045643)
- Record hotplugged USB device in LXC live guest config (rhbz#1045643)
- Fix reset of cgroup when detaching USB device from LXC guests (rhbz#1045643)
- Disks are always block devices, never character devices (rhbz#1045643)
- Move check for cgroup devices ACL upfront in LXC hotplug (rhbz#1045643)
- Add virFileMakeParentPath helper function (rhbz#1045643)
- Add helper for running code in separate namespaces (rhbz#1045643)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC shutdown/reboot code (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC disk hotplug (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC USB hotplug (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC block hostdev hotplug (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC chardev hostdev hotplug (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC hotunplug code (CVE-2013-6456)
- Ignore additional fields in iscsiadm output (rhbz#1067173)
- qemuBuildNicDevStr: Set vectors= on Multiqueue (rhbz#1066209)
- Don't depend on syslog.service (rhbz#1032695)
- libvirt-guests: Run only after libvirtd (rhbz#1032695)
- virSystemdCreateMachine: Set dependencies for slices (rhbz#1032695)
- libvirt-guests: Wait for libvirtd to initialize (rhbz#1032695)
- virNetServerRun: Notify systemd that we're accepting clients (rhbz#1032695)

* Wed Feb 12 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-23
- Generate a valid imagelabel even for type 'none' (rhbz#1061657)
- qemu: keep pre-migration domain state after failed migration (rhbz#1057407)
- schema: Fix guest timer specification schema according to the docs (rhbz#1056205)
- conf: Enforce supported options for certain timers (rhbz#1056205)
- qemu: hyperv: Add support for timer enlightenments (rhbz#1056205)
- build: correctly check for SOICGIFVLAN GET_VLAN_VID_CMD command (rhbz#1062665)
- util: Add "shareable" field for virSCSIDevice struct (rhbz#957292)
- util: Fix the indention (rhbz#957292)
- qemu: Don't fail if the SCSI host device is shareable between domains (rhbz#957292)
- util: Add one argument for several scsi utils (rhbz#957292)
- tests: Add tests for scsi utils (rhbz#957292)
- qemu: Fix the error message for scsi host device's shareable checking (rhbz#957292)
- util: Accept test data path for scsi device's sg_path (rhbz#957292)
- tests: Modify the scsi util tests (rhbz#957292)
- event: move event filtering to daemon (regression fix) (rhbz#1047964)

* Wed Feb  5 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-22
- Add a read/write lock implementation (rhbz#1034807)
- Push nwfilter update locking up to top level (rhbz#1034807)
- utils: Introduce functions for kernel module manipulation (rhbz#1045124)
- virCommand: Introduce virCommandSetDryRun (rhbz#1045124)
- tests: Add test for new virkmod functions (rhbz#1045124)
- Honor blacklist for modprobe command (rhbz#1045124)
- qemu: Be sure we're using the updated value of backend during hotplug (rhbz#1056360)
- network: Permit upstream forwarding of unqualified DNS names (rhbz#1061099)
- network: Only prevent forwarding of DNS requests for unqualified names (rhbz#1061099)
- network: Change default of forwardPlainNames to 'yes' (rhbz#1061099)

* Wed Jan 29 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-21
- util: Correct the NUMA node range checking (rhbz#1045958)
- storage: Add document for possible problem on volume detection (rhbz#726797)
- storage: Fix autostart of pool with "fc_host" type adapter (rhbz#726797)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 1.1.1-20
- Mass rebuild 2014-01-24

* Wed Jan 22 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-19
- CVE-2013-6436: Fix crash in lxcDomainGetMemoryParameters (rhbz#1049137)
- Fix crash in lxcDomainSetMemoryParameters (rhbz#1052062)
- Don't crash if a connection closes early (CVE-2014-1447)
- Really don't crash if a connection closes early (CVE-2014-1447)
- qemu: Change the default unix monitor timeout (rhbz#892273)
- virSecuritySELinuxSetFileconHelper: Don't fail on read-only NFS (rhbz#996543)
- qemu: Avoid operations on NULL monitor if VM fails early (rhbz#1054785)
- virt-login-shell: Fix regressions in behavior (rhbz#1015247)
- pci: Make reattach work for unbound devices (rhbz#1046919)
- pci: Fix failure paths in detach (rhbz#1046919)
- qemu: Don't detach devices if passthrough doesn't work (rhbz#1046919)
- Fix migration with QEMU 1.6 (rhbz#1053405)
- build: More workarounds for if_bridge.h (rhbz#1042937)
- build: Fix build with latest rawhide kernel headers (rhbz#1042937)
- aarch64: Disable -fstack-protector. (rhbz#1042937)
- AArch64: Parse cputopology from /proc/cpuinfo. (rhbz#1042937)
- virDomainEventCallbackListFree: Don't leak @list->callbacks (rhbz#1047964)
- Fix memory leak in virObjectEventCallbackListRemoveID() (rhbz#1047964)
- event: Filter global events by domain:getattr ACL (CVE-2014-0028)
- Doc: Improve the document for nodesuspend (rhbz#1045089)
- Doc: Add "note" for node-memory-tune (rhbz#1045089)

* Wed Jan  8 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-18
- qemu: Ask for -enable-fips when FIPS is required (rhbz#1035474)
- qemu: Properly set MaxMemLock when hotplugging with VFIO (rhbz#1035490)
- qemu: Avoid duplicate security label restore on hostdev attach failure (rhbz#1035490)
- qemu: Re-add hostdev interfaces to hostdev array on libvirtd restart (rhbz#1045002)
- domain: Don't try to interpret <driver> as virtio config for hostdev interfaces (rhbz#1046337)
- virBitmapParse: Fix behavior in case of error and fix up callers (rhbz#1047234)
- qemu: Fix live pinning to memory node on NUMA system (rhbz#1047234)
- qemu: Clean up qemuDomainSetNumaParameters (rhbz#1047234)
- qemu: Range check numa memory placement mode (rhbz#1047234)
- virkeycode: Allow ANSI_A (rhbz#1044806)
- Fix argument order of qemuMigrationPerformJob(). (rhbz#1049338)
- qemu: Do not access stale data in virDomainBlockStats (CVE-2013-6458)
- qemu: Avoid using stale data in virDomainGetBlockInfo (CVE-2013-6458)
- qemu: Fix job usage in qemuDomainBlockJobImpl (CVE-2013-6458)
- qemu: Fix job usage in qemuDomainBlockCopy (rhbz#1048643)
- qemu: Fix job usage in virDomainGetBlockIoTune (CVE-2013-6458)
- PanicCheckABIStability: Need to check for existence (rhbz#996520)
- virsh: Improve usability of '--print-xml' flag for attach-disk command (rhbz#1049529)
- virsh: Don't use legacy API if --current is used on device hot(un)plug (rhbz#1049529)
- virsh: Use inactive definition when removing disk from config (rhbz#1049529)

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.1.1-17
- Mass rebuild 2013-12-27

* Wed Dec 18 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-16
- qemu: Check for reboot-timeout on monitor (rhbz#1042690)
- virsh: Fix return value error of cpu-stats (rhbz#1043388)
- tools: Fix virsh connect man page (rhbz#1043260)
- conf: Introduce generic ISA address (rhbz#996520)
- conf: Add support for panic device (rhbz#996520)
- qemu: Add support for -device pvpanic (rhbz#996520)
- Fix invalid read in virNetSASLSessionClientStep debug log (rhbz#1043864)
- virsh: man: Mention that volumes need to be in storage pool for undefine (rhbz#1044445)

* Fri Dec 13 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-15
- spec: Don't save/restore running VMs on libvirt-client update (rhbz#1033626)
- qemu: hotplug: Only label hostdev after checking device conflicts (rhbz#1025108)
- qemu: hotplug: Fix double free on USB collision (rhbz#1025108)
- qemu: hotplug: Fix adding USB devices to the driver list (rhbz#1025108)
- docs: Enhance memoryBacking/locked documentation (rhbz#1035954)
- util: Fix two virCompareLimitUlong bugs (rhbz#1024272)
- cgroups: Redefine what "unlimited" means wrt memory limits (rhbz#1024272)
- qemu: Report VIR_DOMAIN_MEMORY_PARAM_UNLIMITED properly (rhbz#1024272)
- qemu: Fix minor inconsistency in error message (rhbz#1024272)
- conf: Don't format memtune with unlimited values (rhbz#1024272)
- qemu_process: Read errors from child (rhbz#1035955)
- network: Properly update iptables rules during net-update (rhbz#1035336)
- Tie SASL callbacks lifecycle to virNetSessionSASLContext (rhbz#1039991)
- screenshot: Implement multiple screen support (rhbz#1026966)
- Switch to private redhat namespace for QMP I/O error reason (rhbz#1026966)
- Support virtio disk hotplug in JSON mode (rhbz#1026966)

* Fri Dec  6 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-14
- nodedev: Resolve Relax-NG validity error (rhbz#1035792)
- test-lib: Make case skipping possible (rhbz#1034380)
- tests: Don't test user config file if ran as root (rhbz#1034380)
- Improve cgroups docs to cover systemd integration (rhbz#1004340)
- Fix busy wait loop in LXC container I/O handling (rhbz#1032705)
- tests: Guarantee abs_srcdir in all C tests (rhbz#1035403)
- Introduce standard methods for sorting strings with qsort (rhbz#1035403)
- Add virFileIsMountPoint function (rhbz#1035403)
- Pull lxcContainerGetSubtree out into shared virfile module (rhbz#1035403)
- Fix bug in identifying sub-mounts (rhbz#1035403)
- LXC: Ensure security context is set when mounting images (rhbz#923903)
- Ensure to zero out the virDomainBlockJobInfo arg (rhbz#1028846)
- qemu: Default to vfio for nodedev-detach (rhbz#1035188)
- daemon: Run virStateCleanup conditionally (rhbz#1033061)
- qemu: Add "-boot strict" to commandline whenever possible (rhbz#1037593)
- tests: Add forgotten boot-strict test files (rhbz#1037593)
- conf: Fix XML formatting of RNG device info (rhbz#1035118)
- qemu: Improve error when setting invalid count of vcpus via agent (rhbz#1035108)
- Add qxl ram size to ABI stability check (rhbz#1035123)

* Fri Nov 22 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-13
- virsh-domain: Mark --live and --config mutually exclusive in vcpucount (rhbz#1024245)
- virSecurityLabelDefParseXML: Don't parse label on model='none' (rhbz#1028962)
- qemuMonitorIO: Don't use @mon after it's unrefed (rhbz#1018267)
- qemu: Allow hotplug of multiple SCSI devices (rhbz#1031062)
- qemu: Call qemuSetupHostdevCGroup later during hotplug (rhbz#1025108)
- virscsi: Hostdev SCSI AdapterId retrieval fix (rhbz#1031079)
- storage: Returns earlier if source adapter of the scsi pool is a HBA (rhbz#1027680)
- spec: Restrict virt-login-shell usage (rhbz#1033614)
- spec: Don't save/restore running VMs on libvirt-client update (rhbz#1033626)
- Don't start a nested job in qemuMigrationPrepareAny (rhbz#1018267)

* Fri Nov  8 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-12
- virpci: Don't error on unbinded devices (rhbz#1019387)
- network: Fix connections count in case of allocate failure (rhbz#1020135)
- qemu: Clean up migration ports when migration cancelled (rhbz#1019237)
- qemuMigrationBeginPhase: Check for 'drive-mirror' for NBD (rhbz#1022393)
- Allow root directory in filesystem source dir schema (rhbz#1028107)
- Use a port from the migration range for NBD as well (rhbz#1025699)
- qemu: Avoid double free of VM (rhbz#1018267)
- util: Use size_t instead of unsigned int for num_virtual_functions (rhbz#1025397)
- pci: Properly handle out-of-order SRIOV virtual functions (rhbz#1025397)
- conf: Do better job when comparing features ABI compatibility (rhbz#1008989)
- schema: Rename option 'hypervtristate' to 'featurestate' (rhbz#1008989)
- conf: Mark user provided strings in error messages when parsing XML (rhbz#1008989)
- cpu: Add support for loading and storing CPU data (rhbz#1008989)
- cpu: x86: Rename struct cpuX86cpuid as virCPUx86CPUID (rhbz#1008989)
- cpu: x86: Rename struct cpuX86Data as virCPUx86Data (rhbz#1008989)
- cpu: x86: Rename x86DataFree() as virCPUx86DataFree() (rhbz#1008989)
- Ensure 'arch' is always set in cpuArchNodeData (rhbz#1008989)
- cpu: x86: Rename x86MakeCPUData as virCPUx86MakeData (rhbz#1008989)
- cpu: x86: Rename x86DataAddCpuid as virCPUx86DataAddCPUID (rhbz#1008989)
- cpu: x86: Rename data_iterator and DATA_ITERATOR_INIT (rhbz#1008989)
- cpu: x86: Fix return types of x86cpuidMatch and x86cpuidMatchMasked (rhbz#1008989)
- cpu: x86: Use whitespace to clarify context and use consistent labels (rhbz#1008989)
- cpu: x86: Clean up error messages in x86VendorLoad() (rhbz#1008989)
- cpu: Export few x86-specific APIs (rhbz#1008989)
- cpu: x86: Parse the CPU feature map only once (rhbz#1008989)
- cpu_x86: Refactor storage of CPUID data to add support for KVM features (rhbz#1008989)
- qemu: Add monitor APIs to fetch CPUID data from QEMU (rhbz#1008989)
- cpu: x86: Add internal CPUID features support and KVM feature bits (rhbz#1008989)
- conf: Refactor storing and usage of feature flags (rhbz#1008989)
- qemu: Add support for paravirtual spinlocks in the guest (rhbz#1008989)
- qemu: process: Validate specific CPUID flags of a guest (rhbz#1008989)

* Fri Nov  1 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-11
- Add helpers for getting env vars in a setuid environment (rhbz#1015247)
- Only allow 'stderr' log output when running setuid (CVE-2013-4400)
- Close all non-stdio FDs in virt-login-shell (CVE-2013-4400)
- Don't link virt-login-shell against libvirt.so (CVE-2013-4400)
- build: Fix linking virt-login-shell (rhbz#1015247)
- build: Fix build of virt-login-shell on systems with older gnutls (rhbz#1015247)
- Set a sane $PATH for virt-login-shell (rhbz#1015247)
- spec: Fix rpm build when lxc disabled (rhbz#1015247)
- Move virt-login-shell into libvirt-login-shell sub-RPM (rhbz#1015247)
- Make virCommand env handling robust in setuid env (rhbz#1015247)
- Remove all direct use of getenv (rhbz#1015247)
- Block all use of getenv with syntax-check (rhbz#1015247)
- Only allow the UNIX transport in remote driver when setuid (rhbz#1015247)
- Don't allow remote driver daemon autostart when running setuid (rhbz#1015247)
- Add stub getegid impl for platforms lacking it (rhbz#1015247)
- Remove (nearly) all use of getuid()/getgid() (rhbz#1015247)
- Block all use of libvirt.so in setuid programs (rhbz#1015247)
- spec: Clean up distribution of ChangeLog (and others) (rhbz#1024393)
- Push RPM deps down into libvirt-daemon-driver-XXXX sub-RPMs (rhbz#1024393)

* Wed Oct 23 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-10
- qemu_process: Make qemuProcessReadLog() more versatile and reusable (rhbz#1001738)
- qemu: monitor: Add infrastructure to access VM logs for better err msgs (rhbz#1001738)
- qemu: monitor: Produce better errors on monitor hangup (rhbz#1001738)
- qemu: Wire up better early error reporting (rhbz#1001738)
- qemu: process: Silence coverity warning when rewinding log file (rhbz#1001738)
- qemu: hostdev: Refactor PCI passhrough handling (rhbz#1001738)
- qemu: hostdev: Fix function spacing and header formatting (rhbz#1001738)
- qemu: hostdev: Add checks if PCI passthrough is available in the host (rhbz#1001738)
- qemu: Prefer VFIO for PCI device passthrough (rhbz#1001738)
- qemu: Init @pcidevs in qemuPrepareHostdevPCIDevices (rhbz#1001738)
- Fix max stream packet size for old clients (rhbz#950416)
- Adjust legacy max payload size to account for header information (rhbz#950416)
- rpc: Correct the wrong payload size checking (rhbz#950416)
- qemu: Simplify calling qemuDomainHostdevNetConfigRestore (rhbz#1005682)
- qemu: Move qemuDomainRemoveNetDevice to avoid forward reference (rhbz#1005682)
- qemu: Fix removal of <interface type='hostdev'> (rhbz#1005682)
- remote: Fix regression in event deregistration (rhbz#1020376)
- qemu: managedsave: Add support for compressing managed save images (rhbz#1017227)
- qemu: snapshot: Add support for compressing external snapshot memory (rhbz#1017227)
- Migration: Introduce VIR_MIGRATE_PARAM_LISTEN_ADDRESS (rhbz#1015215)
- virsocket: Introduce virSocketAddrIsWildcard (rhbz#1015215)
- qemu: Implement support for VIR_MIGRATE_PARAM_LISTEN_ADDRESS (rhbz#1015215)
- qemu_conf: Introduce "migration_address" (rhbz#1015215)
- qemu: Include listenAddress in debug prints (rhbz#1015215)
- docs: Expand description of host-model CPU mode (rhbz#1014682)
- qemu: Avoid assigning unavailable migration ports (rhbz#1019237)
- qemu: Make migration port range configurable (rhbz#1019237)
- qemu: Fix augeas support for migration ports (rhbz#1019237)
- Fix perms for virConnectDomainXML{To, From}Native (CVE-2013-4401)

* Tue Oct 15 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-9
- virNetDevBandwidthEqual: Make it more robust (rhbz#1014503)
- qemu_hotplug: Allow QoS update in qemuDomainChangeNet (rhbz#1014503)
- qemu: Check actual netdev type rather than config netdev type during init (rhbz#1012824)
- Fix crash in libvirtd when events are registered & ACLs active (CVE-2013-4399) (rhbz#1011429)
- Remove virConnectPtr arg from virNWFilterDefParse* (rhbz#1015108)
- Don't pass virConnectPtr in nwfilter 'struct domUpdateCBStruct' (rhbz#1015108)
- Remove use of virConnectPtr from all remaining nwfilter code (rhbz#1015108)
- Don't set netdev offline in container cleanup (rhbz#1014604)
- Avoid reporting an error if veth device is already deleted (rhbz#1014604)
- Avoid deleting NULL veth device name (rhbz#1014604)
- Retry veth device creation on failure (rhbz#1014604)
- Use 'vnet' as prefix for veth devices (rhbz#1014604)
- Free cmd in virNetDevVethDelete (rhbz#1014604)
- Free cmd in virNetDevVethCreate (rhbz#1014604)
- LXC: Fix handling of RAM filesystem size units (rhbz#1015689)
- build: Add lxc testcase to dist list (rhbz#1015689)
- tests: Work with older dbus (rhbz#1018730)
- virdbus: Add virDBusHasSystemBus() (rhbz#1018730)
- virsystemd: Don't fail to start VM if DBus isn't available or compiled in (rhbz#1018730)
- DBus: Introduce virDBusIsServiceEnabled (rhbz#1018730)
- Change way we fake dbus method calls (rhbz#1018730)
- Fix virsystemdtest for previous commit (rhbz#1018730)
- LXC: Workaround machined uncleaned data with containers running systemd. (rhbz#1018730)
- Allow use of a private dbus bus connection (rhbz#998365)
- Add a method for closing the dbus system bus connection (rhbz#998365)
- Make LXC controller use a private dbus connection & close it (rhbz#998365)
- Fix flaw in detecting log format (rhbz#927072)
- Fix exit status of lxc controller (rhbz#927072)
- Improve error reporting with LXC controller (rhbz#927072)
- nwfilter: Don't fail to start if DBus isn't available (rhbz#927072)
- Don't ignore all dbus connection errors (rhbz#927072)
- LXC: Check the existence of dir before resolving symlinks (rhbz#927072)
- Ensure lxcContainerMain reports errors on stderr (rhbz#927072)
- Ensure lxcContainerResolveSymlinks reports errors (rhbz#927072)
- Improve log filtering in virLXCProcessReadLogOutputData (rhbz#927072)
- Initialize threading & error layer in LXC controller (rhbz#1018725)
- qemu_migration: Avoid crashing if domain dies too quickly (rhbz#1018267)
- Convert uuid to a string before printing it (rhbz#1019023)

* Wed Oct  2 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-8
- conf: Don't crash on invalid chardev source definition of RNGs and other (rhbz#1012196)
- rpc: Increase bound limit for virDomainGetJobStats (rhbz#1012818)
- qemu: Free all driver data in qemuStateCleanup (rhbz#1011330)
- qemu: Don't leak reference to virQEMUDriverConfigPtr (rhbz#1011330)
- qemu: Eliminate redundant if clauses in qemuCollectPCIAddress (rhbz#1003983)
- qemu: Allow some PCI devices to be attached to PCIe slots (rhbz#1003983)
- qemu: Replace multiple strcmps with a switch on an enum (rhbz#1003983)
- qemu: Support ich9-intel-hda audio device (rhbz#1003983)
- qemu: Turn if into switch in qemuDomainValidateDevicePCISlotsQ35 (rhbz#1003983)
- qemu: Prefer to put a Q35 machine's dmi-to-pci-bridge at 00:1E.0 (rhbz#1003983)

* Wed Sep 25 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-7
- Fix crash in remoteDispatchDomainMemoryStats (CVE-2013-4296)
- LXC: Don't mount securityfs when user namespace enabled (rhbz#872648)
- Move array of mounts out of lxcContainerMountBasicFS (rhbz#872648)
- Ensure root filesystem is recursively mounted readonly (rhbz#872648)
- qemu: Fix seamless SPICE migration (rhbz#1010861)
- qemu: Use "ide" as device name for implicit SATA controller on Q35 (rhbz#1008903)
- qemu: Only parse basename when determining emulator properties (rhbz#1010617)
- qemu: Recognize -machine accel=kvm when parsing native (rhbz#1010617)
- qemu: Don't leave shutdown inhibited on attach failure (rhbz#1010617)
- qemu: Don't leak vm on failure (rhbz#1010617)
- Fix typo in identity code which is pre-requisite for CVE-2013-4311 (rhbz#1006272)

* Thu Sep 19 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-6
- Also store user & group ID values in virIdentity (rhbz#1006272)
- Ensure system identity includes process start time (rhbz#1006272)
- Add support for using 3-arg pkcheck syntax for process (CVE-2013-4311)
- Free slicename in virSystemdCreateMachine (rhbz#1008619)
- qemu: Fix checking of ABI stability when restoring external checkpoints (rhbz#1008340)
- qemu: Use "migratable" XML definition when doing external checkpoints (rhbz#1008340)
- qemu: Fix memleak after commit 59898a88ce8431bd3ea249b8789edc2ef9985827 (rhbz#1008340)
- qemu: Avoid dangling job in qemuDomainSetBlockIoTune (rhbz#700443)

* Sat Sep 14 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-5
- Pass AM_LDFLAGS to driver modules too (rhbz#1006299)
- virsh domjobinfo: Do not return 1 if job is NONE (rhbz#1006864)
- Fix polkit permission names for storage pools, vols & node devices (rhbz#700443)
- Fix naming of permission for detecting storage pools (rhbz#700443)
- security: Provide supplemental groups even when parsing label (CVE-2013-4291) (rhbz#1006513)
- virFileNBDDeviceAssociate: Avoid use of uninitialized variable (CVE-2013-4297)
- Rename "struct interface_driver" to virNetcfDriverState (rhbz#983026)
- netcf driver: Use a single netcf handle for all connections (rhbz#983026)
- virDomainDefParseXML: Set the argument of virBitmapFree to NULL after calling virBitmapFree (rhbz#1006722)
- Add test for the nodemask double free crash (rhbz#1006722)
- qemu: Fix checking of guest ABI compatibility when reverting snapshots (rhbz#1006886)

* Fri Sep  6 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-4
- Don't crash in qemuBuildDeviceAddressStr (rhbz#1003526)
- Fix leaks in python bindings (rhbz#1003828)
- Process virtlockd.conf instead of libvirtd.conf (rhbz#1003685)
- test_virtlockd.aug.in: Use the correct file (rhbz#1003685)
- qemu: Make domain renaming work during migration (rhbz#999352)
- qemu: Handle huge number of queues correctly (rhbz#651941)
- conf: Remove the actual hostdev when removing a network (rhbz#1003537)
- conf: Don't deref NULL actual network in virDomainNetGetActualHostdev() (rhbz#1003537)
- python: Fix a PyList usage mistake (rhbz#1002558)
- Add '<nat>' element to '<forward>' network schemas (rhbz#1004364)
- Always specify qcow2 compat level on qemu-img command line (rhbz#997977)
- selinux: Distinguish failure to label from request to avoid label (rhbz#924153)
- selinux: Enhance test to cover nfs label failure (rhbz#924153)

* Fri Aug 30 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-3
- RPC: Don't accept client if it would overcommit max_clients (rhbz#981729)
- Introduce max_queued_clients (rhbz#981729)
- conf: Add default USB controller in qemu post-parse callback (rhbz#819968)
- qemu: Rename some functions in qemu_command.c (rhbz#819968)
- qemu: Eliminate almost-duplicate code in qemu_command.c (rhbz#819968)
- qemu: Enable auto-allocate of all PCI addresses (rhbz#819968)
- qemu: Add pcie-root controller (rhbz#819968)
- qemu: Add dmi-to-pci-bridge controller (rhbz#819968)
- qemu: Fix handling of default/implicit devices for q35 (rhbz#819968)
- qemu: Properly set/use device alias for pci controllers (rhbz#819968)
- qemu: Enable using implicit sata controller in q35 machines (rhbz#819968)
- qemu: Improve error reporting during PCI address validation (rhbz#819968)
- qemu: Refactor qemuDomainCheckDiskPresence for only disk presence check (rhbz#910171)
- qemu: Add helper functions for diskchain checking (rhbz#910171)
- qemu: Check presence of each disk and its backing file as well (rhbz#910171)
- conf: Add startupPolicy attribute for harddisk (rhbz#910171)
- qemu: Support to drop disk with 'optional' startupPolicy (rhbz#910171)
- Split TLS test into two separate tests (rhbz#994158)
- Avoid re-generating certs every time (rhbz#994158)
- Change data passed into TLS test cases (rhbz#994158)
- Fix validation of CA certificate chains (rhbz#994158)
- Fix parallel runs of TLS test suites (rhbz#994158)
- tests: Fix parallel runs of TLS test suites (rhbz#994158)
- Add a man page for virtlockd daemon (rhbz#991494)
- Add an example config file for virtlockd (rhbz#991494)
- Properly handle -h / -V for --help/--version aliases in virtlockd/libvirtd (rhbz#991494)
- Make check for /dev/loop device names stricter to avoid /dev/loop-control (rhbz#924815)
- Ensure securityfs is mounted readonly in container (rhbz#872642)
- Add info about access control checks into API reference (rhbz#700443)
- Record the where the auto-generated data comes from (rhbz#700443)
- Add documentation for access control system (rhbz#700443)
- virsh-domain: Flip logic in cmdSetvcpus (rhbz#996552)
- Honour root prefix in lxcContainerMountFSBlockAuto (rhbz#924815)
- util: Add virGetUserDirectoryByUID (rhbz#988491)
- Introduce a virt-login-shell binary (rhbz#988491)
- build: Fix compilation of virt-login-shell.c (rhbz#988491)
- Fix double-free and broken logic in virt-login-shell (rhbz#988491)
- Address missed feedback from review of virt-login-shell (rhbz#988491)
- Ensure that /dev exists in the container root filesystem (rhbz#924815)
- remote: Fix a segfault in remoteDomainCreateWithFlags (rhbz#994855)
- build: Avoid -lgcrypt with newer gnutls (rhbz#951637)
- virnettlscontext: Resolve Coverity warnings (UNINIT) (rhbz#994158)
- build: Fix missing max_queued_clients in augeas test file for libvirtd.conf (rhbz#981729)
- virsh-domain: Fix memleak in cmdCPUBaseline (rhbz#997798)
- Fix typo in domain name in polkit acl example (rhbz#700443)
- Update polkit examples to use 'lookup' method (rhbz#700443)
- Add bounds checking on virDomainMigrate*Params RPC calls (CVE-2013-4292) (rhbz#1002667)
- Add bounds checking on virDomainGetJobStats RPC call (rhbz#1002667)
- Add bounds checking on virDomain{SnapshotListAllChildren, ListAllSnapshots} RPC calls (rhbz#1002667)
- Add bounds checking on virConnectListAllDomains RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllStoragePools RPC call (rhbz#1002667)
- Add bounds checking on virStoragePoolListAllVolumes RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllNetworks RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllInterfaces RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllNodeDevices RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllNWFilters RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllSecrets RPC call (rhbz#1002667)
- Prohibit unbounded arrays in XDR protocols (rhbz#1002667)
- virbitmap: Refactor virBitmapParse to avoid access beyond bounds of array (rhbz#997906)
- virbitmaptest: Fix function header formatting (rhbz#997906)
- virbitmaptest: Add test for out of bounds condition (rhbz#997906)
- virsh-domain: Fix memleak in cmdUndefine with storage (rhbz#999057)
- virsh: Modify vshStringToArray to duplicate the elements too (rhbz#999057)
- virsh: Don't leak list of volumes when undefining domain with storage (rhbz#999057)
- Fix URI connect precedence (rhbz#999323)
- tests: Add URI precedence checking (rhbz#999323)
- Don't free NULL network in cmdNetworkUpdate (rhbz#1001094)
- virsh: Fix debugging (rhbz#1001628)
- qemu: Remove hostdev entry when freeing the depending network entry (rhbz#1002669)
- Set security label on FD for virDomainOpenGraphics (rhbz#999925)
- virsh: Free the caps list properly if one of them is invalid (rhbz#1001957)
- virsh: Free the formatting string when listing pool details (rhbz#1001957)
- virsh-pool.c: Don't jump over variable declaration (rhbz#1001957)
- virsh: Free the list from ListAll APIs even for 0 items (rhbz#1001957)
- virsh: Free messages after logging them to a file (rhbz#1001957)
- Reverse logic allowing partial DHCP host XML (rhbz#1001078)
- virsh: Print cephx and iscsi usage (rhbz#1000155)
- qemu_conf: Fix broken logic for adding passthrough iscsi lun (rhbz#1000159)
- Report secret usage error message similarly (rhbz#1000168)
- docs: Update the formatdomain disk examples (rhbz#1000169)
- docs: Update formatsecrets to include more examples of each type (rhbz#1000169)
- docs: Update iSCSI storage pool example (rhbz#1000169)
- docs: Reformat <disk> attribute description in formatdomain (rhbz#1000169)
- qemuBuildNicDevStr: Add mq=on for multiqueue networking (rhbz#651941)
- migration: Do not restore labels on failed migration (rhbz#822052)
- qemu: Drop qemuDomainMemoryLimit (rhbz#1001143)
- docs: Discourage users to set hard_limit (rhbz#1001143)
- docs: Clean 09adfdc62de2b up (rhbz#1001143)
- qemuSetupMemoryCgroup: Handle hard_limit properly (rhbz#1001143)
- qemuBuildCommandLine: Fall back to mem balloon if there's no hard_limit (rhbz#1001143)
- qemuDomainAttachHostPciDevice: Fall back to mem balloon if there's no hard_limit (rhbz#1001143)

* Fri Aug  2 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-2
- spec: Change --enable-werror handling to match upstream
- Delete obsolete / unused python test files (rhbz#884103)
- Remove reference to python/tests from RPM %doc (rhbz#884103)
- spec: Explicitly claim ownership of channel subdir (rhbz#884103)
- Add APIs for formatting systemd slice/scope names (rhbz#980929)
- Add support for systemd cgroup mount (rhbz#980929)
- Cope with races while killing processes (rhbz#980929)
- Enable support for systemd-machined in cgroups creation (rhbz#980929)
- Ensure LXC/QEMU APIs set the filename for errors (rhbz#991348)
- Avoid crash if NULL is passed for filename/funcname in logging (rhbz#991348)

* Tue Jul 30 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-1
- Rebased to libvirt-1.1.1

* Fri Jul 12 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.0-2
- qemu: Fix double free in qemuMigrationPrepareDirect (rhbz#977961)
- Fix crash when multiple event callbacks were registered (CVE-2013-2230)
- Paused domain should remain paused after migration (rhbz#981139)

* Mon Jul  1 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.0-1
- Rebased to libvirt-1.1.0

* Mon Jun  3 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.6-1
- Rebased to libvirt-1.0.6

* Mon May 13 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.5-2
- virInitctlRequest: Don't hardcode 384 bytes size
- network: Fix network driver startup for qemu:///session
- virInitctlRequest: Unbreak make syntax check
- virInitctlRequest: Unbreak make syntax check
- build: Always include sanitytest in tarball
- qemu: Fix stupid typos in VFIO cgroup setup/teardown
- build: Always include libvirt_lxc.syms in tarball
- build: Clean up stray files found by 'make distcheck'
- spec: Proper soft static allocation of qemu uid
- Fix F_DUPFD_CLOEXEC operation args
- build: Fix mingw build of virprocess.c
- Fix potential use of undefined variable in remote dispatch code
- build: Avoid non-portable cast of pthread_t
- Fix release of resources with lockd plugin
- Fixup rpcgen code on kFreeBSD too
- Make detect_scsi_host_caps a function on all architectures
- qemu: Allocate network connections sooner during domain startup
- tests: Files named '.*-invalid.xml' should fail validation
- conf: Don't crash on a tpm device with no backends
- Don't mention disk controllers in generic controller errors
- iscsi: Don't leak portal string when starting a pool
- util: Fix virFileOpenAs return value and resulting error logs

* Thu May  2 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.5-1
- Rebased to libvirt-1.0.5

* Fri Apr 19 2013 Daniel Mach <dmach@redhat.com> - 1.0.4-1.1
- Rebuild for cyrus-sasl

* Mon Apr  8 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.4-1
- Rebased to libvirt-1.0.4

* Mon Apr 08 2013 Richard W.M. Jones <rjones@redhat.com> - 1.0.3-2
- Rebuild against gnutls 3.

* Tue Mar  5 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.3-1
- Rebased to libvirt-1.0.3

* Thu Jan 31 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.2-1
- Rebased to libvirt-1.0.2

* Tue Dec 18 2012 Jiri Denemark <jdenemar@redhat.com> - 1.0.1-1
- Rebased to libvirt-1.0.1

* Wed Nov 14 2012 Jiri Denemark <jdenemar@redhat.com> - 1.0.0-1
- Rebased to libvirt-1.0.0

* Tue Oct 30 2012 Cole Robinson <crobinso@redhat.com> - 0.10.2.1-2
- Disable libxl on F18 too

* Sat Oct 27 2012 Cole Robinson <crobinso@redhat.com> - 0.10.2.1-1
- Rebased to version 0.10.2.1
- Fix lvm volume creation when alloc=0 (bz #866481)
- Clarify virsh send-keys man page example (bz #860004)
- Fix occasional deadlock via virDomainDestroy (bz #859009)
- Fix LXC deadlock from ctrl-c (bz #848119)
- Fix occasional selinux denials with macvtap (bz #798605)
- Fix multilib conflict with systemtap files (bz #831425)
- Don't trigger keytab warning in system logs (bz #745203)
- Fix qemu domxml-2-native NIC model out (bz #636832)
- Fix error message if not enough space for lvm vol (bz #609104)

* Thu Oct 25 2012 Cole Robinson <crobinso@redhat.com> - 0.10.2-4
- Disable libxl driver, since it doesn't build with xen 4.2 in rawhide

* Mon Sep 24 2012 Richard W.M. Jones <rjones@redhat.com> - 0.10.2-3
- Re-add Use-qemu-system-i386-as-binary-instead-of-qemu.patch
  NB: This patch is Fedora-specific and not upstream.
- Add upstream patches: don't duplicate environment variables (RHBZ#859596).

* Mon Sep 24 2012 Daniel Veillard <veillard@redhat.com> - 0.10.2-1
- Upstream release 0.10.2
- network: define new API virNetworkUpdate
- add support for QEmu sandbox support
- blockjob: add virDomainBlockCommit
- New APIs to get/set Node memory parameters
- new API virConnectListAllSecrets
- new API virConnectListAllNWFilters
- new API virConnectListAllNodeDevices
- parallels: add support of containers to the driver
- new API virConnectListAllInterfaces
- new API virConnectListAllNetworks
- new API virStoragePoolListAllVolumes
- Add PMSUSPENDED life cycle event
- new API virStorageListAllStoragePools
- Add per-guest S3/S4 state configuration
- qemu: Support for Block Device IO Limits
- a lot of bug fixes, improvements and portability work

* Fri Sep 21 2012 Richard W.M. Jones <rjones@redhat.com> - 0.10.1-5
- Add (upstream) patches to label sockets for SELinux (RHBZ#853393).

* Thu Sep 13 2012 Richard W.M. Jones <rjones@redhat.com> - 0.10.1-4
- Fix for 32 bit qemu renamed to qemu-system-i386 (RHBZ#857026).

* Wed Sep 12 2012 Cole Robinson <crobinso@redhat.com> - 0.10.1-3
- Fix libvirtd segfault with old netcf-libs (bz 853381)
- Drop unneeded dnsmasq --filterwin2k
- Fix unwanted connection closing, needed for boxes

* Wed Sep  5 2012 Daniel P. Berrange <berrange@redhat.com> - 0.10.1-2
- Remove dep on ceph RPM (rhbz #854360)

* Fri Aug 31 2012 Daniel Veillard <veillard@redhat.com> - 0.10.1-1
- upstream release of 0.10.1
- many fixes from 0.10.0

* Wed Aug 29 2012 Daniel Veillard <veillard@redhat.com> - 0.10.0-1
- upstream release of 0.10.0
- agent: add qemuAgentArbitraryCommand() for general qemu agent command
- Introduce virDomainPinEmulator and virDomainGetEmulatorPinInfo functions
- network: use firewalld instead of iptables, when available
- network: make network driver vlan-aware
- esx: Implement network driver
- driver for parallels hypervisor
- Various LXC improvements
- Add virDomainGetHostname
- a lot of bug fixes, improvements and portability work

* Thu Aug 23 2012 Daniel Veillard <veillard@redhat.com> - 0.10.0-0rc1
- release candidate 1 of 0.10.0

* Tue Aug 14 2012 Daniel P. Berrange <berrange@redhat.com> - 0.10.0-0rc0.2
- Enable autotools to make previous patch work

* Tue Aug 14 2012 Daniel Veillard <veillard@redhat.com> - 0.10.0-0rc0.1
- fix security driver missing from the daemon

* Wed Aug  8 2012 Daniel Veillard <veillard@redhat.com> - 0.10.0-0rc0
- snapshot before 0.10.0 in a few weeks
- adds the parallel driver support

* Mon Jul 23 2012 Richard W.M. Jones <rjones@redhat.com> - 0.9.13-3
- Add upstream patch to fix RHBZ#842114.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul  2 2012 Daniel Veillard <veillard@redhat.com> - 0.9.13-1
- S390: support for s390(x)
- snapshot: implement new APIs for esx and vbox
- snapshot: new query APIs and many improvements
- virsh: Allow users to reedit rejected XML
- nwfilter: add DHCP snooping
- Enable driver modules in libvirt RPM
- Default to enable driver modules for libvirtd
- storage backend: Add RBD (RADOS Block Device) support
- sVirt support for LXC domains inprovement
- a lot of bug fixes, improvements and portability work

* Mon May 14 2012 Daniel Veillard <veillard@redhat.com> - 0.9.12-1
- qemu: allow snapshotting of sheepdog and rbd disks
- blockjob: add new APIs
- a lot of bug fixes, improvements and portability work

* Thu Apr 26 2012 Cole Robinson <crobinso@redhat.com> - 0.9.11.3-1
- Rebased to version 0.9.11.3
- Abide URI username when connecting to hypervisor (bz 811397)
- Fix managed USB mode (bz 814866)
- Fix crash connecting to ESX host (bz 811891)

* Wed Apr  4 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.11-1
- Update to 0.9.11 release

* Tue Apr  3 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.10-4
- Revert previous change

* Sat Mar 31 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.10-3
- Refactor RPM spec to allow install without default configs

* Thu Mar 15 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.10-2
- Rebuild for libparted soname break

* Mon Feb 13 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.10-1
- Update to 0.9.10

* Thu Jan 12 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.9-2
- Fix LXC I/O handling

* Sat Jan  7 2012 Daniel Veillard <veillard@redhat.com> - 0.9.9-1
- Add API virDomain{S,G}etInterfaceParameters
- Add API virDomain{G, S}etNumaParameters
- Add support for ppc64 qemu
- Support Xen domctl v8
- many improvements and bug fixes

* Thu Dec  8 2011 Daniel P. Berrange <berrange@redhat.com> - 0.9.8-2
- Fix install of libvirt-guests.service & libvirtd.service

* Thu Dec  8 2011 Daniel Veillard <veillard@redhat.com> - 0.9.8-1
- Add support for QEMU 1.0
- Add preliminary PPC cpu driver
- Add new API virDomain{Set, Get}BlockIoTune
- block_resize: Define the new API
- Add a public API to invoke suspend/resume on the host
- various improvements for LXC containers
- Define keepalive protocol and add virConnectIsAlive API
- Add support for STP and VLAN filtering
- many improvements and bug fixes

* Mon Nov 14 2011 Justin M. Forbes <jforbes@redhat.com> - 0.9.7-3
- Remove versioned buildreq for yajl as 2.0.x features are not required.

* Thu Nov 10 2011 Daniel P. Berrange <berrange@redhat.com> - 0.9.7-2
- Rebuild for yajl 2.0.1

* Tue Nov  8 2011 Daniel P. Berrange <berrange@redhat.com> - 0.9.7-1
- Update to 0.9.7 release

* Tue Oct 11 2011 Dan Horák <dan[at]danny.cz> - 0.9.6-3
- xenlight available only on Xen arches (#745020)

* Mon Oct  3 2011 Laine Stump <laine@redhat.com> - 0.9.6-2
- Make PCI multifunction support more manual - Bug 742836
- F15 build still uses cgconfig - Bug 738725

* Thu Sep 22 2011 Daniel Veillard <veillard@redhat.com> - 0.9.6-1
- Fix the qemu reboot bug and a few others bug fixes

* Tue Sep 20 2011 Daniel Veillard <veillard@redhat.com> - 0.9.5-1
- many snapshot improvements (Eric Blake)
- latency: Define new public API and structure (Osier Yang)
- USB2 and various USB improvements (Marc-André Lureau)
- storage: Add fs pool formatting (Osier Yang)
- Add public API for getting migration speed (Jim Fehlig)
- Add basic driver for Microsoft Hyper-V (Matthias Bolte)
- many improvements and bug fixes

* Wed Aug  3 2011 Daniel Veillard <veillard@redhat.com> - 0.9.4-1
- network bandwidth QoS control
- Add new API virDomainBlockPull*
- save: new API to manipulate save file images
- CPU bandwidth limits support
- allow to send NMI and key event to guests
- new API virDomainUndefineFlags
- Implement code to attach to external QEMU instances
- bios: Add support for SGA
- various missing python binding
- many improvements and bug fixes

* Sat Jul 30 2011 Dan Hor?k <dan[at]danny.cz> - 0.9.3-3
- xenlight available only on Xen arches

* Wed Jul  6 2011 Peter Robinson <pbrobinson@gmail.com> - 0.9.3-2
- Add ARM to NUMA platform excludes

* Mon Jul  4 2011 Daniel Veillard <veillard@redhat.com> - 0.9.3-1
- new API virDomainGetVcpupinInfo
- Add TXT record support for virtual DNS service
- Support reboots with the QEMU driver
- New API virDomainGetControlInfo API
- New API virNodeGetMemoryStats
- New API virNodeGetCPUTime
- New API for send-key
- New API virDomainPinVcpuFlags
- support multifunction PCI device
- lxc: various improvements
- many improvements and bug fixes

* Wed Jun 29 2011 Richard W.M. Jones <rjones@redhat.com> - 0.9.2-3
- Rebuild because of libparted soname bump (libparted.so.0 -> libparted.so.1).

* Tue Jun 21 2011 Laine Stump <laine@redhat.com> - 0.9.2-2
- add rule to require netcf-0.1.8 during build so that new transactional
  network change APIs are included.
- document that CVE-2011-2178 has been fixed (by virtue of rebase
  to 0.9.2 - see https://bugzilla.redhat.com/show_bug.cgi?id=709777)

* Mon Jun  6 2011 Daniel Veillard <veillard@redhat.com> - 0.9.2-1
- Framework for lock manager plugins
- API for network config change transactions
- flags for setting memory parameters
- virDomainGetState public API
- qemu: allow blkstat/blkinfo calls during migration
- Introduce migration v3 API
- Defining the Screenshot public API
- public API for NMI injection
- Various improvements and bug fixes

* Wed May 25 2011 Richard W.M. Jones <rjones@redhat.com> - 0.9.1-3
- Add upstream patches:
    0001-json-Avoid-passing-large-positive-64-bit-integers-to.patch
    0001-qemudDomainMemoryPeek-change-ownership-selinux-label.patch
    0002-remote-remove-bogus-virDomainFree.patch
  so that users can try out virt-dmesg.
- Change /var/cache mode to 0711.

* Thu May  5 2011 Daniel Veillard <veillard@redhat.com> - 0.9.1-1
- support various persistent domain updates
- improvements on memory APIs
- Add virDomainEventRebootNew
- various improvements to libxl driver
- Spice: support audio, images and stream compression
- Various improvements and bug fixes

* Thu Apr  7 2011 Daniel Veillard <veillard@redhat.com> - 0.9.0-1
- Support cputune cpu usage tuning
- Add public APIs for storage volume upload/download
- Add public API for setting migration speed on the fly
- Add libxenlight driver
- qemu: support migration to fd
- libvirt: add virDomain{Get,Set}BlkioParameters
- setmem: introduce a new libvirt API (virDomainSetMemoryFlags)
- Expose event loop implementation as a public API
- Dump the debug buffer to libvirtd.log on fatal signal
- Audit support
- Various improvements and bug fixes

* Mon Mar 14 2011 Daniel Veillard <veillard@redhat.com> - 0.8.8-3
- fix a lack of API check on read-only connections
- CVE-2011-1146

* Mon Feb 21 2011 Daniel P. Berrange <berrange@redhat.com> - 0.8.8-2
- Fix kernel boot with latest QEMU

* Thu Feb 17 2011 Daniel Veillard <veillard@redhat.com> - 0.8.8-1
- expose new API for sysinfo extraction
- cgroup blkio weight support
- smartcard device support
- qemu: Support per-device boot ordering
- Various improvements and bug fixes

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jan  6 2011 Daniel Veillard <veillard@redhat.com> - 0.8.7-1
- Preliminary support for VirtualBox 4.0
- IPv6 support
- Add VMware Workstation and Player driver driver
- Add network disk support
- Various improvements and bug fixes
- from 0.8.6:
- Add support for iSCSI target auto-discovery
- QED: Basic support for QED images
- remote console support
- support for SPICE graphics
- sysinfo and VMBIOS support
- virsh qemu-monitor-command
- various improvements and bug fixes

* Fri Oct 29 2010 Daniel Veillard <veillard@redhat.com> - 0.8.5-1
- Enable JSON and netdev features in QEMU >= 0.13
- framework for auditing integration
- framework DTrace/SystemTap integration
- Setting the number of vcpu at boot
- Enable support for nested SVM
- Virtio plan9fs filesystem QEMU
- Memory parameter controls
- various improvements and bug fixes

* Wed Sep 29 2010 jkeating - 0.8.4-3
- Rebuilt for gcc bug 634757

* Thu Sep 16 2010 Dan Horák <dan[at]danny.cz> - 0.8.4-2
- disable the nwfilterxml2xmltest also on s390(x)

* Mon Sep 13 2010 Daniel Veillard <veillard@redhat.com> - 0.8.4-1
- Upstream release 0.8.4

* Mon Aug 23 2010 Daniel P. Berrange <berrange@redhat.com> - 0.8.3-2
- Fix potential overflow in boot menu code

* Mon Aug 23 2010 Daniel P. Berrange <berrange@redhat.com> - 0.8.3-1
- Upstream release 0.8.3

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.8.2-3
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Mon Jul 12 2010 Daniel P. Berrange <berrange@redhat.com> - 0.8.2-2
- CVE-2010-2237 ignoring defined main disk format when looking up disk backing stores
- CVE-2010-2238 ignoring defined disk backing store format when recursing into disk
  image backing stores
- CVE-2010-2239 not setting user defined backing store format when creating new image
- CVE-2010-2242 libvirt: improperly mapped source privileged ports may allow for
  obtaining privileged resources on the host

* Mon Jul  5 2010 Daniel Veillard <veillard@redhat.com> - 0.8.2-1
- Upstream release 0.8.2
- phyp: adding support for IVM
- libvirt: introduce domainCreateWithFlags API
- add 802.1Qbh and 802.1Qbg switches handling
- Support for VirtualBox version 3.2
- Init script for handling guests on shutdown/boot
- qemu: live migration with non-shared storage for kvm

* Fri Apr 30 2010 Daniel Veillard <veillard@redhat.com> - 0.8.1-1
- Upstream release 0.8.1
- Starts dnsmasq from libvirtd with --dhcp-hostsfile
- Add virDomainGetBlockInfo API to query disk sizing
- a lot of bug fixes and cleanups

* Mon Apr 12 2010 Daniel Veillard <veillard@redhat.com> - 0.8.0-1
- Upstream release 0.8.0
- Snapshotting support (QEmu/VBox/ESX)
- Network filtering API
- XenAPI driver
- new APIs for domain events
- Libvirt managed save API
- timer subselection for domain clock
- synchronous hooks
- API to update guest CPU to host CPU
- virDomainUpdateDeviceFlags new API
- migrate max downtime API
- volume wiping API
- and many bug fixes

* Tue Mar 30 2010 Richard W.M. Jones <rjones@redhat.com> - 0.7.7-3.fc14
- No change, just rebuild against new libparted with bumped soname.

* Mon Mar 22 2010 Cole Robinson <crobinso@redhat.com> - 0.7.7-2.fc14
- Fix USB devices by product with security enabled (bz 574136)
- Set kernel/initrd in security driver, fixes some URL installs (bz 566425)

* Fri Mar  5 2010 Daniel Veillard <veillard@redhat.com> - 0.7.7-1
- macvtap support
- async job handling
- virtio channel
- computing baseline CPU
- virDomain{Attach,Detach}DeviceFlags
- assorted bug fixes and lots of cleanups

* Tue Feb 16 2010 Adam Jackson <ajax@redhat.com> 0.7.6-2
- libvirt-0.7.6-add-needed.patch: Fix FTBFS from --no-add-needed
- Add BuildRequires: xmlrpc-c-client for libxmlrpc_client.so

* Wed Feb  3 2010 Daniel Veillard <veillard@redhat.com> - 0.7.6-1
- upstream release of 0.7.6
- Use QEmu new device adressing when possible
- Implement CPU topology support for QEMU driver
- Implement SCSI controller hotplug/unplug for QEMU
- Implement support for multi IQN
- a lot of fixes and improvements

* Thu Jan 14 2010 Chris Weyl <cweyl@alumni.drew.edu> 0.7.5-3
- bump for libssh2 rebuild

* Tue Jan 12 2010 Daniel P. Berrange <berrange@redhat.com> - 0.7.5-2
- Rebuild for libparted soname change

* Wed Dec 23 2009 Daniel Veillard <veillard@redhat.com> - 0.7.5-1
- Add new API virDomainMemoryStats
- Public API and domain extension for CPU flags
- vbox: Add support for version 3.1
- Support QEMU's virtual FAT block device driver
- a lot of fixes

* Fri Nov 20 2009 Daniel Veillard <veillard@redhat.com> - 0.7.4-1
- upstream release of 0.7.4
- udev node device backend
- API to check object properties
- better QEmu monitor processing
- MAC address based port filtering for qemu
- support IPv6 and multiple addresses per interfaces
- a lot of fixes

* Thu Nov 19 2009 Daniel P. Berrange <berrange@redhat.com> - 0.7.2-6
- Really fix restore file labelling this time

* Wed Nov 11 2009 Daniel P. Berrange <berrange@redhat.com> - 0.7.2-5
- Disable numactl on s390[x]. Again.

* Wed Nov 11 2009 Daniel P. Berrange <berrange@redhat.com> - 0.7.2-4
- Fix QEMU save/restore permissions / labelling

* Thu Oct 29 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.2-3
- Avoid compressing small log files (#531030)

* Thu Oct 29 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.2-2
- Make libvirt-devel require libvirt-client, not libvirt
- Fix qemu machine types handling

* Wed Oct 14 2009 Daniel Veillard <veillard@redhat.com> - 0.7.2-1
- Upstream release of 0.7.2
- Allow to define ESX domains
- Allows suspend and resulme of LXC domains
- API for data streams
- many bug fixes

* Tue Oct 13 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-12
- Fix restore of qemu guest using raw save format (#523158)

* Fri Oct  9 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-11
- Fix libvirtd memory leak during error reply sending (#528162)
- Add several PCI hot-unplug typo fixes from upstream

* Tue Oct  6 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-10
- Create /var/log/libvirt/{lxc,uml} dirs for logrotate
- Make libvirt-python dependon on libvirt-client
- Sync misc minor changes from upstream spec

* Tue Oct  6 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-9
- Change logrotate config to weekly (#526769)

* Thu Oct  1 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-8
- Disable sound backend, even when selinux is disabled (#524499)
- Re-label qcow2 backing files (#497131)

* Wed Sep 30 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-7
- Fix USB device passthrough (#522683)

* Mon Sep 21 2009 Chris Weyl <cweyl@alumni.drew.edu> - 0.7.1-6
- rebuild for libssh2 1.2

* Mon Sep 21 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-5
- Don't set a bogus error in virDrvSupportsFeature()
- Fix raw save format

* Thu Sep 17 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-4
- A couple of hot-unplug memory handling fixes (#523953)

* Thu Sep 17 2009 Daniel Veillard <veillard@redhat.com> - 0.7.1-3
- disable numactl on s390[x]

* Thu Sep 17 2009 Daniel Veillard <veillard@redhat.com> - 0.7.1-2
- revamp of spec file for modularity and RHELs

* Tue Sep 15 2009 Daniel Veillard <veillard@redhat.com> - 0.7.1-1
- Upstream release of 0.7.1
- ESX, VBox driver updates
- mutipath support
- support for encrypted (qcow) volume
- compressed save image format for Qemu/KVM
- QEmu host PCI device hotplug support
- configuration of huge pages in guests
- a lot of fixes

* Mon Sep 14 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-0.2.gitfac3f4c
- Update to newer snapshot of 0.7.1
- Stop libvirt using untrusted 'info vcpus' PID data (#520864)
- Support relabelling of USB and PCI devices
- Enable multipath storage support
- Restart libvirtd upon RPM upgrade

* Sun Sep  6 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-0.1.gitg3ef2e05
- Update to pre-release git snapshot of 0.7.1
- Drop upstreamed patches

* Wed Aug 19 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.0-6
- Fix migration completion with newer versions of qemu (#516187)

* Wed Aug 19 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.0-5
- Add PCI host device hotplug support
- Allow PCI bus reset to reset other devices (#499678)
- Fix stupid PCI reset error message (bug #499678)
- Allow PM reset on multi-function PCI devices (bug #515689)
- Re-attach PCI host devices after guest shuts down (bug #499561)
- Fix list corruption after disk hot-unplug
- Fix minor 'virsh nodedev-list --tree' annoyance

* Thu Aug 13 2009 Daniel P. Berrange <berrange@redhat.com> - 0.7.0-4
- Rewrite policykit support (rhbz #499970)
- Log and ignore NUMA topology problems (rhbz #506590)

* Mon Aug 10 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.0-3
- Don't fail to start network if ipv6 modules is not loaded (#516497)

* Thu Aug  6 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.0-2
- Make sure qemu can access kernel/initrd (bug #516034)
- Set perms on /var/lib/libvirt/boot to 0711 (bug #516034)

* Wed Aug  5 2009 Daniel Veillard <veillard@redhat.com> - 0.7.0-1
- ESX, VBox3, Power Hypervisor drivers
- new net filesystem glusterfs
- Storage cloning for LVM and Disk backends
- interface implementation based on netcf
- Support cgroups in QEMU driver
- QEmu hotplug NIC support
- a lot of fixes

* Fri Jul  3 2009 Daniel Veillard <veillard@redhat.com> - 0.6.5-1
- release of 0.6.5

* Fri May 29 2009 Daniel Veillard <veillard@redhat.com> - 0.6.4-1
- release of 0.6.4
- various new APIs

* Fri Apr 24 2009 Daniel Veillard <veillard@redhat.com> - 0.6.3-1
- release of 0.6.3
- VirtualBox driver

* Fri Apr  3 2009 Daniel Veillard <veillard@redhat.com> - 0.6.2-1
- release of 0.6.2

* Wed Mar  4 2009 Daniel Veillard <veillard@redhat.com> - 0.6.1-1
- release of 0.6.1

* Sat Jan 31 2009 Daniel Veillard <veillard@redhat.com> - 0.6.0-1
- release of 0.6.0

* Tue Nov 25 2008 Daniel Veillard <veillard@redhat.com> - 0.5.0-1
- release of 0.5.0

* Tue Sep 23 2008 Daniel Veillard <veillard@redhat.com> - 0.4.6-1
- release of 0.4.6

* Mon Sep  8 2008 Daniel Veillard <veillard@redhat.com> - 0.4.5-1
- release of 0.4.5

* Wed Jun 25 2008 Daniel Veillard <veillard@redhat.com> - 0.4.4-1
- release of 0.4.4
- mostly a few bug fixes from 0.4.3

* Thu Jun 12 2008 Daniel Veillard <veillard@redhat.com> - 0.4.3-1
- release of 0.4.3
- lots of bug fixes and small improvements

* Tue Apr  8 2008 Daniel Veillard <veillard@redhat.com> - 0.4.2-1
- release of 0.4.2
- lots of bug fixes and small improvements

* Mon Mar  3 2008 Daniel Veillard <veillard@redhat.com> - 0.4.1-1
- Release of 0.4.1
- Storage APIs
- xenner support
- lots of assorted improvements, bugfixes and cleanups
- documentation and localization improvements

* Tue Dec 18 2007 Daniel Veillard <veillard@redhat.com> - 0.4.0-1
- Release of 0.4.0
- SASL based authentication
- PolicyKit authentication
- improved NUMA and statistics support
- lots of assorted improvements, bugfixes and cleanups
- documentation and localization improvements

* Sun Sep 30 2007 Daniel Veillard <veillard@redhat.com> - 0.3.3-1
- Release of 0.3.3
- Avahi support
- NUMA support
- lots of assorted improvements, bugfixes and cleanups
- documentation and localization improvements

* Tue Aug 21 2007 Daniel Veillard <veillard@redhat.com> - 0.3.2-1
- Release of 0.3.2
- API for domains migration
- APIs for collecting statistics on disks and interfaces
- lots of assorted bugfixes and cleanups
- documentation and localization improvements

* Tue Jul 24 2007 Daniel Veillard <veillard@redhat.com> - 0.3.1-1
- Release of 0.3.1
- localtime clock support
- PS/2 and USB input devices
- lots of assorted bugfixes and cleanups
- documentation and localization improvements

* Mon Jul  9 2007 Daniel Veillard <veillard@redhat.com> - 0.3.0-1
- Release of 0.3.0
- Secure remote access support
- unification of daemons
- lots of assorted bugfixes and cleanups
- documentation and localization improvements

* Fri Jun  8 2007 Daniel Veillard <veillard@redhat.com> - 0.2.3-1
- Release of 0.2.3
- lot of assorted bugfixes and cleanups
- support for Xen-3.1
- new scheduler API

* Tue Apr 17 2007 Daniel Veillard <veillard@redhat.com> - 0.2.2-1
- Release of 0.2.2
- lot of assorted bugfixes and cleanups
- preparing for Xen-3.0.5

* Thu Mar 22 2007 Jeremy Katz <katzj@redhat.com> - 0.2.1-2.fc7
- don't require xen; we don't need the daemon and can control non-xen now
- fix scriptlet error (need to own more directories)
- update description text

* Fri Mar 16 2007 Daniel Veillard <veillard@redhat.com> - 0.2.1-1
- Release of 0.2.1
- lot of bug and portability fixes
- Add support for network autostart and init scripts
- New API to detect the virtualization capabilities of a host
- Documentation updates

* Fri Feb 23 2007 Daniel P. Berrange <berrange@redhat.com> - 0.2.0-4.fc7
- Fix loading of guest & network configs

* Fri Feb 16 2007 Daniel P. Berrange <berrange@redhat.com> - 0.2.0-3.fc7
- Disable kqemu support since its not in Fedora qemu binary
- Fix for -vnc arg syntax change in 0.9.0  QEMU

* Thu Feb 15 2007 Daniel P. Berrange <berrange@redhat.com> - 0.2.0-2.fc7
- Fixed path to qemu daemon for autostart
- Fixed generation of <features> block in XML
- Pre-create config directory at startup

* Wed Feb 14 2007 Daniel Veillard <veillard@redhat.com> 0.2.0-1.fc7
- support for KVM and QEmu
- support for network configuration
- assorted fixes

* Mon Jan 22 2007 Daniel Veillard <veillard@redhat.com> 0.1.11-1.fc7
- finish inactive Xen domains support
- memory leak fix
- RelaxNG schemas for XML configs

* Wed Dec 20 2006 Daniel Veillard <veillard@redhat.com> 0.1.10-1.fc7
- support for inactive Xen domains
- improved support for Xen display and vnc
- a few bug fixes
- localization updates

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 0.1.9-2
- rebuild against python 2.5

* Wed Nov 29 2006 Daniel Veillard <veillard@redhat.com> 0.1.9-1
- better error reporting
- python bindings fixes and extensions
- add support for shareable drives
- add support for non-bridge style networking
- hot plug device support
- added support for inactive domains
- API to dump core of domains
- various bug fixes, cleanups and improvements
- updated the localization

* Tue Nov  7 2006 Daniel Veillard <veillard@redhat.com> 0.1.8-3
- it's pkgconfig not pgkconfig !

* Mon Nov  6 2006 Daniel Veillard <veillard@redhat.com> 0.1.8-2
- fixing spec file, added %%dist, -devel requires pkgconfig and xen-devel
- Resolves: rhbz#202320

* Mon Oct 16 2006 Daniel Veillard <veillard@redhat.com> 0.1.8-1
- fix missing page size detection code for ia64
- fix mlock size when getting domain info list from hypervisor
- vcpu number initialization
- don't label crashed domains as shut off
- fix virsh man page
- blktapdd support for alternate drivers like blktap
- memory leak fixes (xend interface and XML parsing)
- compile fix
- mlock/munlock size fixes

* Fri Sep 22 2006 Daniel Veillard <veillard@redhat.com> 0.1.7-1
- Fix bug when running against xen-3.0.3 hypercalls
- Fix memory bug when getting vcpus info from xend

* Fri Sep 22 2006 Daniel Veillard <veillard@redhat.com> 0.1.6-1
- Support for localization
- Support for new Xen-3.0.3 cdrom and disk configuration
- Support for setting VNC port
- Fix bug when running against xen-3.0.2 hypercalls
- Fix reconnection problem when talking directly to http xend

* Tue Sep  5 2006 Jeremy Katz <katzj@redhat.com> - 0.1.5-3
- patch from danpb to support new-format cd devices for HVM guests

* Tue Sep  5 2006 Daniel Veillard <veillard@redhat.com> 0.1.5-2
- reactivating ia64 support

* Tue Sep  5 2006 Daniel Veillard <veillard@redhat.com> 0.1.5-1
- new release
- bug fixes
- support for new hypervisor calls
- early code for config files and defined domains

* Mon Sep  4 2006 Daniel Berrange <berrange@redhat.com> - 0.1.4-5
- add patch to address dom0_ops API breakage in Xen 3.0.3 tree

* Mon Aug 28 2006 Jeremy Katz <katzj@redhat.com> - 0.1.4-4
- add patch to support paravirt framebuffer in Xen

* Mon Aug 21 2006 Daniel Veillard <veillard@redhat.com> 0.1.4-3
- another patch to fix network handling in non-HVM guests

* Thu Aug 17 2006 Daniel Veillard <veillard@redhat.com> 0.1.4-2
- patch to fix virParseUUID()

* Wed Aug 16 2006 Daniel Veillard <veillard@redhat.com> 0.1.4-1
- vCPUs and affinity support
- more complete XML, console and boot options
- specific features support
- enforced read-only connections
- various improvements, bug fixes

* Wed Aug  2 2006 Jeremy Katz <katzj@redhat.com> - 0.1.3-6
- add patch from pvetere to allow getting uuid from libvirt

* Wed Aug  2 2006 Jeremy Katz <katzj@redhat.com> - 0.1.3-5
- build on ia64 now

* Thu Jul 27 2006 Jeremy Katz <katzj@redhat.com> - 0.1.3-4
- don't BR xen, we just need xen-devel

* Thu Jul 27 2006 Daniel Veillard <veillard@redhat.com> 0.1.3-3
- need rebuild since libxenstore is now versionned

* Mon Jul 24 2006 Mark McLoughlin <markmc@redhat.com> - 0.1.3-2
- Add BuildRequires: xen-devel

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.1.3-1.1
- rebuild

* Tue Jul 11 2006 Daniel Veillard <veillard@redhat.com> 0.1.3-1
- support for HVM Xen guests
- various bugfixes

* Mon Jul  3 2006 Daniel Veillard <veillard@redhat.com> 0.1.2-1
- added a proxy mechanism for read only access using httpu
- fixed header includes paths

* Wed Jun 21 2006 Daniel Veillard <veillard@redhat.com> 0.1.1-1
- extend and cleanup the driver infrastructure and code
- python examples
- extend uuid support
- bug fixes, buffer handling cleanups
- support for new Xen hypervisor API
- test driver for unit testing
- virsh --conect argument

* Mon Apr 10 2006 Daniel Veillard <veillard@redhat.com> 0.1.0-1
- various fixes
- new APIs: for Node information and Reboot
- virsh improvements and extensions
- documentation updates and man page
- enhancement and fixes of the XML description format

* Tue Feb 28 2006 Daniel Veillard <veillard@redhat.com> 0.0.6-1
- added error handling APIs
- small bug fixes
- improve python bindings
- augment documentation and regression tests

* Thu Feb 23 2006 Daniel Veillard <veillard@redhat.com> 0.0.5-1
- new domain creation API
- new UUID based APIs
- more tests, documentation, devhelp
- bug fixes

* Fri Feb 10 2006 Daniel Veillard <veillard@redhat.com> 0.0.4-1
- fixes some problems in 0.0.3 due to the change of names

* Wed Feb  8 2006 Daniel Veillard <veillard@redhat.com> 0.0.3-1
- changed library name to libvirt from libvir, complete and test the python
  bindings

* Sun Jan 29 2006 Daniel Veillard <veillard@redhat.com> 0.0.2-1
- upstream release of 0.0.2, use xend, save and restore added, python bindings
  fixed

* Wed Nov  2 2005 Daniel Veillard <veillard@redhat.com> 0.0.1-1
- created
