#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
	echo "Usage:"
	echo "	packbootiso.sh <boot.iso> <kdump_addon_tarball>"
	echo "	# make sure you have mkisofs, iso-info and mksquashfs installed"
	exit 1
fi 

boot_iso=$1
addon_tarball=$2
label=$(iso-info $boot_iso |grep Volume|cut -d':' -f2)
label=$(echo $label)

mkdir mnt

mount -o loop $boot_iso mnt
cp -ar mnt isodir
umount mnt

mount -o loop isodir/LiveOS/squashfs.img mnt
cp -ar mnt squashdir 
umount mnt

mount -o loop squashdir/LiveOS/rootfs.img mnt
tar -xvzf $addon_tarball 
mkdir -p mnt/usr/share/anaconda/addons
cp -aRf kdump-anaconda-addon/com_redhat_kdump mnt/usr/share/anaconda/addons/
make -C kdump-anaconda-addon/po install DESTDIR=../../mnt
umount mnt
rm -rf kdump-anaconda-addon

cd squashdir
rm ../isodir/LiveOS/squashfs.img
mksquashfs LiveOS ../isodir/LiveOS/squashfs.img -keep-as-directory
cd ..
rm -rf squashdir

cd isodir
mkisofs -o ../boot-1.iso -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -R -J -V "$label" -r .
cd ..

rm -rf isodir mnt
