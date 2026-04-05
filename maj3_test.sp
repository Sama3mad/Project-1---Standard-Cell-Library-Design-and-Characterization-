* MAJ3 debug test v3
.lib /home/sama/work/pdks/volare/sky130/versions/dd7771c384ed36b91a25e9f8b314355fc26561be/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.temp 25
.include cells.lib

VDD vdd 0 1.8

* A starts HIGH, goes LOW at 1n
* B=C=1 held constant
* When A=B=C=1: output=0. When A falls to 0: output should rise to 1
VA asig 0 PULSE(1.8 0 1n 10p 10p 5n 12n)
VB bsig 0 1.8
VC csig 0 1.8
XDUT asig bsig csig y_out vdd 0 maj3x1
CL y_out 0 0.0094p

.tran 1p 12n

.control
run
meas tran cell_rise trig v(asig) val=0.9 fall=1 targ v(y_out) val=0.9 rise=1
meas tran rise_tran trig v(y_out) val=0.36 rise=1 targ v(y_out) val=1.44 rise=1
print cell_rise rise_tran
plot v(asig) v(y_out)
.endc
.end
