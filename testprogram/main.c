#include <stdint.h>

__attribute__((noinline, used)) void
marker(uint32_t id)
{
    asm volatile(".byte 0x0F, 0x04\n\t"
                 ".word 0x5a\n\t"
                 :
                 : "D"(id)
                 : "memory");
}

int
main(void)
{
    marker(1);

    return 0;
}
