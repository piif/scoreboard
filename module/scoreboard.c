// adapted copy/paste from https://github.com/richardghirst/Panalyzer/blob/master/pandriver.c
// for compilation see http://blogsmayan.blogspot.fr/p/programming-interrupts-in-raspberry-pi.html
// or https://digibird1.wordpress.com/raspberry-pi-as-an-oscilloscope-10-msps/

#include <linux/module.h>
//#include <linux/string.h>
#include <linux/fs.h>
#include <linux/io.h>
//#include <linux/vmalloc.h>
#include <linux/cdev.h>
//#include <mach/platform.h>
//#include <asm/uaccess.h>

static int dev_open(struct inode *, struct file *);
static int dev_close(struct inode *, struct file *);
static ssize_t dev_read(struct file *, char *, size_t, loff_t *);
static ssize_t dev_write(struct file *, const char *, size_t, loff_t *);

static struct file_operations fops =  {
	.open = dev_open,
	.read = dev_read,
	.write = dev_write,
	.release = dev_close,
};

//static volatile uint32_t *data;
//static volatile uint32_t *ticker;
//static volatile uint32_t *armtick;

#define DEBUG(msg, ...) printk(msg, ##__VA_ARGS__)

static dev_t devno;
static struct cdev my_cdev;

uint16_t charToBits(char c) {
	switch(c) {
	case '-': return 0x040; // '00 0100 0000'
	case '0': return 0x03F; // '00 0011 1111'
	case '1': return 0x006; // '00 0000 0110'
	case '2': return 0x05B; // '00 0101 1011'
	case '3': return 0x04F; // '00 0100 1111'
	case '4': return 0x066; // '00 0110 0110'
	case '5': return 0x06D; // '00 0110 1101'
	case '6': return 0x07D; // '00 0111 1101'
	case '7': return 0x007; // '00 0000 0111'
	case '8': return 0x07F; // '00 0111 1111'
	case '9': return 0x06F; // '00 0110 1111'
	case ' ': return 0x000; // '00 0000 0000'
	case 'Z': return 0x200; // '10 0000 0000' = buzzer on
	default : return 0x000;
	}
}

/**
static int send_data(uint8_t len, uint8_t *buffer) {
	local_irq_disable();
	local_fiq_disable();
	start_time = *ticker;
	start_tick = armtick[8];

	// len * 10 loops
	for (;len;len--, buffer++) {
		uint16_t bits = charToBits(*buffer);
		for(uint16_t mask = 0x200; mask; mask>>=1) {
			do { t1 = *ticker; } while (t1 == t);
			// clock + one bit to send to *data
			*data = (bits & mask ? 1 : 0);
		}
	}

	end_tick = armtick[8];
	local_fiq_enable();
	local_irq_enable();

	return 0;
}
**/
int init_module(void) {
	int res, my_major;

	res = alloc_chrdev_region(&devno, 0, 1, "scoreboard");
	if (res < 0) {
		printk(KERN_WARNING "scoreboard: Can't allocated device number\n");
		return res;
	}
	my_major = MAJOR(devno);

	cdev_init(&my_cdev, &fops);
	my_cdev.owner = THIS_MODULE;
	my_cdev.ops = &fops;
	res = cdev_add(&my_cdev, MKDEV(my_major, 0), 1);
	if (res) {
		printk(KERN_WARNING "scoreboard: Error %d adding device\n", res);
		unregister_chrdev_region(devno, 1);
		return res;
	} else {
		printk("scoreboard: device %d:0 ready\n", my_major);
	}

	// TODO : send LOW to clock

//	data = (uint32_t *)ioremap(0x20200034, 4);
//	ticker = (uint32_t *)ioremap(0x20003004, 4);
//	armtick = (uint32_t *)ioremap(0x2000b400, 0x24);

	return 0;
}


void cleanup_module(void) {
//	iounmap(data);
//	iounmap(ticker);
//	iounmap(armtick);
	cdev_del(&my_cdev);
	unregister_chrdev_region(devno, 1);
	DEBUG("scoreboard: module unloaded\n");
}


static int dev_open(struct inode *inod,struct file *fil) {
	DEBUG("scoreboard: device open\n");

	return 0;
}

// not used ?
static ssize_t dev_read(struct file *filp,char *buf,size_t count,loff_t *f_pos) {
	DEBUG("scoreboard: device read ignored\n");

	return count;
}

static ssize_t dev_write(struct file *filp, const char *buf, size_t count, loff_t *f_pos) {
	DEBUG("scoreboard: device write %d bytes from %d\n", count, (int)(*f_pos));

	while(*f_pos < count) {
		DEBUG("scoreboard: device write byte %d\n", buf[*f_pos]);
		(*f_pos)++;
	}
	return count; // or count - initial value of *f_pos ?
}

static int dev_close(struct inode *inod,struct file *fil) {
	DEBUG("scoreboard: device close\n");
	return 0;
}

MODULE_DESCRIPTION("ScoreBoard, RaspberryPi synchronous serial sender");
MODULE_AUTHOR("Christian Lefebvre <christian_lefebvre@laposte.net>");
MODULE_LICENSE("GPL v2");
