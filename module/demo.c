#include <linux/module.h>  /* Needed by all modules */
 
MODULE_LICENSE("GPL");
MODULE_AUTHOR("sylvain@chicoree.fr, 2012");
MODULE_DESCRIPTION("Demo module for cross compiling");
 
int init_module(void)
{
  // Print a message in the kernel log
  printk("Hello world\n");
 
  // A non 0 return means init_module failed; module can't be loaded.
  return 0;
}
 
 
void cleanup_module(void)
{
  // Print a message in the kernel log
  printk("Goodbye world\n");
}
