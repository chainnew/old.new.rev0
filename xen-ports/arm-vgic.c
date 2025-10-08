/*
 * ARM64 Virtual GICv3 (VGIC) implementation for Xen guests
 * Ported from x86 virtual APIC
 */

#include <xen/sched.h>
#include <xen/irq.h>
#include <xen/softirq.h>
#include <asm/gic_v3_defs.h>
#include <asm/vgic.h>
#include <asm/p2m.h>

/* VGIC register emulation for guest access */
struct vgic_v3 {
    /* Distributor state */
    uint32_t gicd_ctlr;
    uint32_t gicd_typer;
    uint32_t gicd_isenabler[32];
    uint32_t gicd_icenabler[32];
    uint32_t gicd_ipriorityr[256];
    
    /* Redistributor per-CPU state */
    uint32_t gicr_ctlr;
    uint32_t gicr_waker;
    
    /* Pending/active IRQs */
    unsigned long pending_irqs[BITS_TO_LONGS(1024)];
    unsigned long active_irqs[BITS_TO_LONGS(1024)];
};

/* Initialize VGIC for a domain */
int vgic_v3_init(struct domain *d)
{
    struct vgic_v3 *vgic;
    
    vgic = xzalloc(struct vgic_v3);
    if (!vgic)
        return -ENOMEM;
    
    /* Initialize distributor */
    vgic->gicd_ctlr = 0;
    vgic->gicd_typer = (1023 << 5); /* 1024 IRQs */
    
    d->arch.vgic = vgic;
    
    printk("VGIC: Initialized for domain %d\n", d->domain_id);
    return 0;
}

/* Inject virtual interrupt to guest */
void vgic_inject_irq(struct domain *d, unsigned int virq)
{
    struct vgic_v3 *vgic = d->arch.vgic;
    
    if (virq >= 1024)
        return;
    
    /* Set pending bit */
    set_bit(virq, vgic->pending_irqs);
    
    /* Trigger vCPU for interrupt delivery */
    vgic_vcpu_inject_irq(d->vcpu[0], virq);
}

/* EOI handling from guest */
void vgic_eoi_irq(struct vcpu *v, unsigned int virq)
{
    struct vgic_v3 *vgic = v->domain->arch.vgic;
    
    /* Clear active bit */
    clear_bit(virq, vgic->active_irqs);
    
    /* Re-sample if level-triggered */
    if (test_bit(virq, vgic->pending_irqs))
        vgic_vcpu_inject_irq(v, virq);
}

/* Register read emulation */
uint32_t vgic_read_reg(struct vcpu *v, paddr_t addr)
{
    struct vgic_v3 *vgic = v->domain->arch.vgic;
    
    /* Distributor registers */
    if (addr >= GICD_BASE && addr < GICD_BASE + 0x10000) {
        switch (addr - GICD_BASE) {
        case GICD_CTLR:
            return vgic->gicd_ctlr;
        case GICD_TYPER:
            return vgic->gicd_typer;
        /* ... more registers */
        }
    }
    
    return 0;
}

/* Register write emulation */
void vgic_write_reg(struct vcpu *v, paddr_t addr, uint32_t val)
{
    struct vgic_v3 *vgic = v->domain->arch.vgic;
    
    if (addr >= GICD_BASE && addr < GICD_BASE + 0x10000) {
        switch (addr - GICD_BASE) {
        case GICD_CTLR:
            vgic->gicd_ctlr = val & 0x3; /* Enable bits */
            break;
        /* ... more registers */
        }
    }
}
