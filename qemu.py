import os
import sys

precmd=""
basecmd="qemu-system-x86_64 -nodefaults -accel kvm -monitor stdio -bios /usr/share/OVMF/x64/OVMF.fd -cpu host -device usb-ehci -device usb-tablet"
idctr=0
args=[]

cdef=False
vdef=False
mdef=False
run=True

osargs=sys.argv

i=0
while (i<len(osargs)):
    match(osargs[i]):
        case "-drive":
            i+=1
            args.append(f"-drive file={osargs[i]},format=raw,id=id{idctr},if=none -device nvme,drive=id{idctr},serial=nvme_{idctr}")
            idctr+=1
        case "-usb":
            i+=1
            args.append(f"-device usb-ehci -drive file={osargs[i]},format=raw,id=id{idctr},if=none -device usb-storage,drive=id{idctr},serial=usb_{idctr}")
            idctr+=1
        case "-cd":
            i+=1
            args.append(f"-drive file={osargs[i]},format=raw,id=id{idctr},if=none -device ide-cd,drive=id{idctr},serial=cdrom_{idctr}")
            idctr+=1
        case "-net":
            args.append(f"-netdev user,id=id{idctr} -device e1000,netdev=id{idctr}")
            idctr+=1
        case "-tor":
            args.append(f"-netdev 'user,restrict=on,guestfwd=tcp:10.0.2.4:9050-cmd:nc 127.0.0.1 9050,guestfwd=tcp:10.0.2.4:53-cmd:nc -u 1.1.1.1 53,id=id{idctr}' -device e1000,netdev=id{idctr}")
            idctr+=1
        case "-netfwd":
            i+=1
            ports=osargs[i].split(",")
            fwd=""
            for x in ports:
                p=x.split(":")
                fwd+=f"hostfwd=::{p[0]}-:{p[1]},"
            args.append(f"-netdev user,{fwd}id=id{idctr} -device e1000,netdev=id{idctr}")
            idctr+=1
        case "-cores":
            i+=1
            args.append(f"-smp {osargs[i]}")
            cdef=True
        case "-video":
            i+=1
            args.append(f"-device {osargs[i]}-vga")
            vdef=True
        case "-mem":
            i+=1
            args.append(f"-m {osargs[i]}")
            mdef=True
        case "-audio":
            args.append(f"-device ich9-intel-hda -audiodev sdl,id=id{idctr} -device hda-duplex,audiodev=id{idctr}")
            idctr+=1
        case "--help":
            print("Help:\n\
                    -drive [vhd name] // adds a drive to the virtual machine\n\
                    -cd [iso name] // adds a virtual disk image to the machine\n\
                    -usb [image name] // adds a virtual usb stick to the vm\n\
                    -net // adds network to the machine\n\
                    -tor // adds a network adapter which can only connect to the tor proxy running on the local system (on port 9050) and for dns services the port 53 to cloudflare dns\n\
                    -netfwd [{dst port}:{src port},{...}] // adds network with port forwarding\n\
                    -audio // adds audio\n\
                    -cores [corecount] // specifies the corecount of the machine, default 4\n\
                    -video [device name] // specifies the video driver, default virtio\n\
                    -mem [size (.../G/M/K)] // specifies virtual memory, default 8G\n\
                    \n\
                    requirements for this script:\n\
                    - tor\n\
                    - netcat\n\
                    - qemu\n\
                    - python")
            run=False
    i+=1

if (vdef == False): args.append("-device virtio-vga")
if (cdef == False): args.append("-smp 4")
if (mdef == False): args.append("-m 8G")


i=0
while (i<len(args)):
    basecmd+=f" {args[i]}"
    i+=1

print(basecmd)
if (run): os.system(basecmd)
