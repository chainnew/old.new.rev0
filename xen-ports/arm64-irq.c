/*
 * Xen ARM64 IRQ management and routing
 * Ported/adapted from x86/irq.c for GICv3 distributor (GICD) and redistributor (GICR)
 */
#include <xen/init.h>
#include <xen/irq.h>
#include <xen/sched.h>
#include <xen/percpu.h>
#include <xen/softirq.h>
#include <asm/gic_v3_defs.h>
#include <asm/gic_v3.h>
#include <asm/p2m.h>

/* IRQ descriptor structure - preserved from x86 logic */
struct irq_desc {
    unsigned int            irq;
    struct radix_tree_root  action_list;  /* Preserved for event channel compat */
    cpumask_t               *affinity;    /* CPU affinity mask */
    bool                    is_gic_sgi;   /* Flag for SGI vs PPI/SPI */
    /* GICv3 specific fields */
    uint32_t                gic_irq_type; /* GIC IRQ type: EDGE or LEVEL */
    struct gic_channel      *gic_channel; /* Channel for routing */
};

/* Global IRQ descriptor table - shared logic */
static DEFINE_RADIX_TREE(irq_descs, GFP_KERNEL);

/* GICv3 globals */
static struct gic_v3 *gic;
static uint32_t nr_irqs = 1024; /* Configurable, default for GICv3 */

/* Initialize IRQ subsystem for ARM64/GICv3 */
void __init irq_init(void)
{
    int i;

    /* Initialize GICv3 distributor and redistributors */
    gic = gic_v3_init();  /* Alloc and map GICD/GICR */
    if (!gic) {
        panic("Failed to initialize GICv3");
    }

    /* Enable distributor */
    gicv3_dist_init(gic);

    /* Initialize per-CPU redistributors */
    for_each_present_cpu(i) {
        gicv3_rdist_cpu_init(smp_processor_id(), gic);
    }

    /* Initialize IRQ descriptor tree - preserved from x86 */
    INIT_RADIX_TREE(&irq_descs, GFP_KERNEL);

    /* Reserve low IRQs for SGIs (0-15) and PPIs (16-31) */
    for (i = 0; i < 32; i++) {
        struct irq_desc *desc = xzalloc(struct irq_desc);
        if (!desc)
            continue;
        desc->irq = i;
        desc->is_gic_sgi = (i < 16);
        desc->affinity = &cpu_online_mask;
        radix_tree_insert(&irq_descs, i, desc);
    }

    /* Enable GIC system interrupts */
    gicv3_cpuif_enable();

    printk("GICv3 IRQ subsystem initialized with %u IRQs\n", nr_irqs);
}

/* Route IRQ to specific vCPU - adapted for GICv3 target list routing */
int irq_route_to_guest(struct domain *d, unsigned int irq, unsigned int vcpu_id)
{
    struct irq_desc *desc;
    struct vcpu *v = d->vcpu[vcpu_id];
    unsigned int target_cpu = v->processor;

    desc = radix_tree_lookup(&irq_descs, irq);
    if (!desc) {
        return -EINVAL;
    }

    /* For SGIs: Direct inject via ICC_SGI1R_EL1 */
    if (desc->is_gic_sgi) {
        uint64_t sgi_reg = (1ULL << 40) | /* NS */
                           (irq & 0xf) << 24 | /* SGI ID */
                           (1ULL << (target_cpu + 16)); /* Target list: single CPU */
        asm volatile("msr " __stringify(ICC_SGI1R_EL1) ", %0" : : "r" (sgi_reg));
        isb();
        return 0;
    }

    /* For PPI/SPI: Set affinity via GICD_IROUTER */
    if (irq < 32) { /* PPI */
        /* PPIs are per-CPU, route via redistributor */
        gicv3_rdist_route_ppi(target_cpu, irq, desc->gic_irq_type);
    } else { /* SPI */
        /* Route via distributor target list */
        gicv3_dist_route_spi(gic, irq, target_cpu, desc->gic_irq_type);
        /* Comment: GICv3 uses 32-bit target list registers (GICD_IROUTERn),
         * where bits 63:56 are affinity level 3 (cluster), 55:48 aff2, etc.
         * For single CPU routing, set aff3=0, aff2=0, aff1=0, aff0=target_cpu,
         * and CPUID bit. This preserves x86's per-vCPU routing logic. */
    }

    /* Update affinity mask - preserved logic */
    cpumask_set_cpu(target_cpu, desc->affinity);

    return 0;
}

/* Bind IRQ to action - preserved from x86, with GIC enable */
int bind_irq_to_guest(unsigned int irq, struct domain *d)
{
    struct irq_desc *desc;

    desc = radix_tree_lookup(&irq_descs, irq);
    if (!desc)
        return -EINVAL;

    /* Enable IRQ in GICD_ISENABLER */
    if (irq >= 32) { /* SPI */
        gicv3_dist_enable_spi(gic, irq);
    } else if (irq >= 16) { /* PPI */
        gicv3_rdist_enable_ppi(smp_processor_id(), irq);
    }
    /* SGIs always enabled */

    /* Add to action list - x86 preserved */
    /* ... (radix tree insert action) */

    return 0;
}

/* Handle IRQ - entry point, adapted for GICv3 ack/eoi */
void do_IRQ(unsigned int irq)
{
    struct irq_desc *desc = radix_tree_lookup(&irq_descs, irq);

    if (!desc)
        return;

    /* Acknowledge IRQ in GIC */
    gicv3_ack_irq(irq);  /* Writes to ICC_IAR_EL1, reads IRQ ID */

    /* Dispatch to handler - preserved logic */
    /* ... (call action handlers) */

    /* EOI to GIC */
    gicv3_eoi_irq(irq);  /* Writes to ICC_EOIR_EL1 */
}

/* Early init hook */
early_initcall(irq_init);
