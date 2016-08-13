
ifeq (${PI_KERNEL},)
  $(error PI_KERNEL variable must be defined to point to pi kernel sources)
endif

obj-m := demo.o
PWD := $(shell pwd)

CROSS_OPTIONS:=ARCH=arm CROSS_COMPILE=arm-linux-gnu-

all: Module.symvers
	$(MAKE) -C $(PI_KERNEL) M=$(PWD) ${CROSS_OPTIONS} modules
clean:
	$(MAKE) -C $(PI_KERNEL) M=$(PWD) ${CROSS_OPTIONS} clean

Module.symvers:
	ln -sf ${PI_KERNEL}/Module.symvers Module.symvers