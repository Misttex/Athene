import sys
import libvirt

conn = None
try:
	conn = libvirt.open("qemu:///system")
	domains = conn.listAllDomains(0)
	if len(domains) != 0:
		for domain in domains:
			print(' '+domain.name())
	else:
		print(' None')

except libvirt.libvirtError as e:
	print(reper(e),file=sys.stderr)
	exit(1)

conn.close()
