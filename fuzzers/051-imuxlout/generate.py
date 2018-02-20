#!/usr/bin/env python3

import sys, re, os

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

tiledata = dict()
pipdata = dict()
ignpip = set()

print("Loading tags from design.txt.")
with open("design.txt", "r") as f:
    for line in f:
        tile, pip, src, dst, pnum, pdir = line.split()
        _, pip = pip.split(".")
        _, src = src.split("/")
        _, dst = dst.split("/")
        pnum = int(pnum)
        pdir = int(pdir)

        if tile not in tiledata:
            tiledata[tile] = {"pips": set(), "srcs": set(), "dsts": set()}

        if pip in pipdata:
            assert pipdata[pip] == (src, dst)
        else:
            pipdata[pip] = (src, dst)

        tiledata[tile]["pips"].add(pip)
        tiledata[tile]["srcs"].add(src)
        tiledata[tile]["dsts"].add(dst)

        if pdir == 0:
            tiledata[tile]["srcs"].add(dst)
            tiledata[tile]["dsts"].add(src)

        if pnum == 1 or pdir == 0 or \
                re.match(r"^(L[HV]B?|G?CLK)(_L)?(_B)?[0-9]", src) or \
                re.match(r"^(L[HV]B?|G?CLK)(_L)?(_B)?[0-9]", dst) or \
                re.match(r"^(CTRL|GFAN)(_L)?[0-9]", dst):
            ignpip.add(pip)

for tile, pips_srcs_dsts in tiledata.items():
    pips = pips_srcs_dsts["pips"]
    srcs = pips_srcs_dsts["srcs"]
    dsts = pips_srcs_dsts["dsts"]

    for pip, src_dst in pipdata.items():
        src, dst = src_dst
        if pip in ignpip:
            pass
        elif pip in pips:
            segmk.addtag(tile, "%s.%s" % (dst, src), 1)
        elif src_dst[1] not in dsts:
            segmk.addtag(tile, "%s.%s" % (dst, src), 0)


def bitfilter(frame_idx, bit_idx):
    assert os.getenv("XRAY_DATABASE") in ["artix7", "kintex7"]
    if frame_idx in [30, 31]:
        return False
    return True


segmk.compile(bitfilter=bitfilter)
segmk.write()