* Logic verification testbench
.lib /home/sama/work/pdks/volare/sky130/versions/dd7771c384ed36b91a25e9f8b314355fc26561be/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.temp 25
.include cells.lib

VDD vdd 0 1.8
VA  a   0 PULSE(0 1.8 0    0 0 10n 20n)
VB  b   0 PULSE(0 1.8 5n   0 0 10n 20n)
VC  c   0 PULSE(0 1.8 2.5n 0 0 5n  10n)

XINV1  a     y_inv1 vdd 0 invx1
XNAND  a b   y_nand vdd 0 nand2x1
XNOR   a b   y_nor  vdd 0 nor2x1
XMAJ   a b c y_maj  vdd 0 maj3x1

.tran 100p 40n

.control
run
plot v(a) v(b) v(c) v(y_inv1) v(y_nand) v(y_nor) v(y_maj)
.endc
.end
