/*
 * ARM64 Xen PV Guest Enlightenment
 * Ported from x86 enlighten.c for paravirtualization support
 */

#include <linux/kernel.h>
#include <linux/string.h>
#include <linux/types.h>

#include <asm/irq.h>
#include <asm/page.h>
#include <asm/smp.h>
#include <asm/xen/hypercall.h>
#include <asm/xen/hypervisor.h>
#include <xen/events.h>
#include <xen/grant_table.h>
#include <xen/interface/xen.h>
#include <xen/interface/version.h>
#include <xen/page.h>

extern shared_info_t *HYPERVISOR_shared_info;
extern struct start_info *xen_start_info;

/* ARM64-specific: Use HVC for hypercalls */
#define HYPERCALL_HVC 0xd4000002  /* HVC #0 instruction */

static void __init xen_banner(void)
{
    unsigned version = xen_start_info->version;
    pr_info("Xen version %d.%d%s.\n",
            (version >> 16) & 0xff, version & 0xff,
            xen_start_info->flags & SIF_PRIVILEGED ? " (Dom0)" : "");
}

/* Initialize shared info page mapping */
void __init xen_arch_pre_setup_events(void)
{
    HYPERVISOR_shared_info = __va(xen_start_info->shared_info);
    if (!HYPERVISOR_shared_info)
        panic("xen: Unable to map shared info page\n");
    
    xen_banner();
}

/* Setup event channels */
int __init xen_arch_init_events(void)
{
    int rc;
    
    rc = xen_evtchn_init();
    if (rc) {
        pr_err("Xen: Failed to initialize event channels (%d)\n", rc);
        return rc;
    }
    
    /* ARM64: Use GIC PPI for event channel delivery */
    if (xen_have_vector_callback) {
        int irq = bind_evtchn_to_irqhandler(0, xen_hvm_callback_vector, 
                                           0, "evtchn", NULL);
        if (irq >= 0)
            pr_info("Xen: Event channel IRQ %d\n", irq);
    }
    
    return 0;
}

/* Grant table initialization */
void __init xen_arch_init_grant_tables(void)
{
    int rc;
    
    if (xen_start_info->nr_grant_frames > 0) {
        gnttab_max_grant_frames = xen_start_info->nr_grant_frames;
        pr_info("Xen: Grant tables using %u frames\n", 
                gnttab_max_grant_frames);
    }
    
    rc = gnttab_init();
    if (rc)
        panic("xen: gnttab_init() failed (%d)\n", rc);
}

/* Initialize hypercall page with HVC stubs */
void __init xen_hypercall_page_init(void)
{
    unsigned long addr = __get_free_pages(GFP_KERNEL | __GFP_ZERO, 0);
    if (!addr)
        panic("Xen: Failed to allocate hypercall page\n");
    
    /* Encode HVC stubs */
    uint32_t *page = (uint32_t *)addr;
    int i;
    for (i = 0; i < NR_hypercalls; i++) {
        page[i] = HYPERCALL_HVC;
    }
    
    xen_hypercall_page = (void *)addr;
    pr_info("Xen: Hypercall page at %p\n", xen_hypercall_page);
}

/* Overall PV guest initialization */
void __init xen_pv_guest_init(void)
{
    xen_arch_pre_setup_events();
    if (xen_arch_init_events())
        panic("Xen: Event channel init failed\n");
    xen_arch_init_grant_tables();
    xen_hypercall_page_init();
    
    xen_init_features();
}

EXPORT_SYMBOL(xen_pv_guest_init);
