/*
 * ARM64 HPET-equivalent implementation using Generic Timers
 * Ported from x86 HPET for Xen hypervisor compatibility
 */

#include <xen/init.h>
#include <xen/time.h>
#include <xen/irq.h>
#include <xen/softirq.h>
#include <asm/io.h>
#include <asm/sysregs.h>
#include <asm/gic.h>

/* ARM Generic Timer registers (EL2 view) */
#define CNTPCT_EL2   "CNTPCT_EL0"    /* Physical counter (read-only) */
#define CNTFRQ_EL0   "CNTFRQ_EL0"    /* Counter frequency */
#define CNTP_TVAL_EL2 "CNTP_TVAL_EL0" /* Timer value */
#define CNTP_CTL_EL2 "CNTP_CTL_EL0"  /* Timer control */
#define CNTP_CVAL_EL2 "CNTP_CVAL_EL0" /* Timer compare value */

/* Timer control bits */
#define CNTP_CTL_ENABLE   (1 << 0)
#define CNTP_CTL_IMASK    (1 << 1)
#define CNTP_CTL_ISTATUS  (1 << 2)

static bool hpet_enabled = false;
static uint64_t timer_freq = 0;
static unsigned int timer_irq = 30; /* GIC PPI 30 for physical timer */

/* Read ARM generic counter (equivalent to HPET counter read) */
uint64_t hpet_read_counter(void)
{
    uint64_t cnt;
    asm volatile("mrs %0, " CNTPCT_EL2 : "=r" (cnt));
    return cnt;
}

/* Get timer frequency (equivalent to HPET capability register) */
static uint64_t arch_timer_get_cntfrq(void)
{
    uint64_t freq;
    asm volatile("mrs %0, " CNTFRQ_EL0 : "=r" (freq));
    return freq;
}

/* Initialize HPET-equivalent timer */
static int __init hpet_init(void)
{
    /* Get counter frequency */
    timer_freq = arch_timer_get_cntfrq();
    if (!timer_freq) {
        printk("ARM generic timer: Invalid frequency\n");
        return -ENODEV;
    }

    printk("ARM generic timer: Frequency %lu Hz\n", timer_freq);

    /* Enable timer control */
    uint64_t cntp_ctl;
    asm volatile("mrs %0, " CNTP_CTL_EL2 : "=r" (cntp_ctl));
    cntp_ctl |= CNTP_CTL_ENABLE;
    cntp_ctl &= ~CNTP_CTL_IMASK; /* Unmask interrupts */
    asm volatile("msr " CNTP_CTL_EL2 ", %0" : : "r" (cntp_ctl));

    /* Route timer IRQ to Xen via GIC */
    if (gic_route_irq_to_xen(timer_irq, "timer-phys") < 0) {
        printk("Failed to route timer IRQ %u\n", timer_irq);
        return -ENODEV;
    }

    hpet_enabled = true;
    return 0;
}

/* Set timer (equivalent to HPET comparator write) */
void hpet_set_timer(uint64_t delta_ns)
{
    if (!hpet_enabled)
        return;

    /* Convert nanoseconds to timer ticks */
    uint64_t ticks = (delta_ns * timer_freq) / 1000000000ULL;
    
    /* Set timer value (countdown) */
    asm volatile("msr " CNTP_TVAL_EL2 ", %0" : : "r" (ticks));
    
    /* Ensure timer is enabled */
    uint64_t cntp_ctl;
    asm volatile("mrs %0, " CNTP_CTL_EL2 : "=r" (cntp_ctl));
    if (!(cntp_ctl & CNTP_CTL_ENABLE)) {
        cntp_ctl |= CNTP_CTL_ENABLE;
        asm volatile("msr " CNTP_CTL_EL2 ", %0" : : "r" (cntp_ctl));
    }
    
    isb(); /* Instruction barrier */
}

/* Timer interrupt handler */
void hpet_timer_handler(int irq, void *dev_id)
{
    /* Clear interrupt status by reading control register */
    uint64_t cntp_ctl;
    asm volatile("mrs %0, " CNTP_CTL_EL2 : "=r" (cntp_ctl));
    
    /* Unmask if needed */
    cntp_ctl &= ~CNTP_CTL_IMASK;
    asm volatile("msr " CNTP_CTL_EL2 ", %0" : : "r" (cntp_ctl));

    /* Raise softirq for timer processing */
    raise_softirq(TIMER_SOFTIRQ);

    /* EOI to GIC */
    gic_eoi_irq(irq);
}

/* Disable HPET */
void hpet_shutdown(void)
{
    if (!hpet_enabled)
        return;

    /* Disable timer */
    uint64_t cntp_ctl;
    asm volatile("mrs %0, " CNTP_CTL_EL2 : "=r" (cntp_ctl));
    cntp_ctl &= ~CNTP_CTL_ENABLE;
    asm volatile("msr " CNTP_CTL_EL2 ", %0" : : "r" (cntp_ctl));

    hpet_enabled = false;
}

/* Register initcall */
__initcall(hpet_init);
