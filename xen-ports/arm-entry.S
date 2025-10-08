/*
 * Xen ARM64 hypervisor low-level entry points.
 * Ported from x86 IDT-based handling to ARM64 exception vectors with GICv3 vectoring.
 *
 * This file defines the exception vector table for EL2 (hypervisor) and basic IRQ
 * handling. On interrupt, the vector table directs to handlers that acknowledge
 * the interrupt via GICv3 (ICC_IAR1_EL1) and dispatch based on INTID.
 * Register save/restore follows ARM64 vector entry protocol (x0-x30, sp, PSTATE).
 * Preserves hypervisor logic: save guest state, handle in C if needed, ERET to resume.
 */

#include <asm/asm_defns.h>
#include <asm/p2m.h>  /* For guest context if needed */
#include <xen/config.h>

/* Macro to save all general-purpose registers (callee-saved and temps) */
.macro save_all
    stp     x29, x30, [sp, #-16]!   // Save frame pointer and link register
    stp     x27, x28, [sp, #-16]!
    stp     x25, x26, [sp, #-16]!
    stp     x23, x24, [sp, #-16]!
    stp     x21, x22, [sp, #-16]!
    stp     x19, x20, [sp, #-16]!
    stp     x17, x18, [sp, #-16]!
    stp     x15, x16, [sp, #-16]!
    stp     x13, x14, [sp, #-16]!
    stp     x11, x12, [sp, #-16]!
    stp     x9,  x10, [sp, #-16]!
    stp     x7,  x8,  [sp, #-16]!
    stp     x5,  x6,  [sp, #-16]!
    stp     x3,  x4,  [sp, #-16]!
    stp     x1,  x2,  [sp, #-16]!
    str     x0,         [sp, #-16]! // x0 last, as it's volatile
    mrs     x0, esr_el2             // Save ESR_EL2 (syndrome) to x0 temp
    mrs     x1, far_el2             // Save FAR_EL2 (fault address)
    mrs     x2, elr_el2             // Save ELR_EL2 (return address)
    mrs     x3, spsr_el2            // Save SPSR_EL2 (saved program state)
    stp     x0, x1, [sp, #-16]!     // Save ESR/FAR
    stp     x2, x3, [sp, #-16]!     // Save ELR/SPSR
.endm

/* Macro to restore all registers and ERET */
.macro restore_all
    ldp     x2, x3, [sp], #16       // Restore ELR/SPSR
    msr     elr_el2, x2
    msr     spsr_el2, x3
    ldp     x0, x1, [sp], #16       // Restore ESR/FAR (discard if not needed)
    ldr     x0, [sp], #16           // Restore x0
    ldp     x1, x2, [sp], #16
    ldp     x3, x4, [sp], #16
    ldp     x5, x6, [sp], #16
    ldp     x7, x8, [sp], #16
    ldp     x9, x10, [sp], #16
    ldp     x11, x12, [sp], #16
    ldp     x13, x14, [sp], #16
    ldp     x15, x16, [sp], #16
    ldp     x17, x18, [sp], #16
    ldp     x19, x20, [sp], #16
    ldp     x21, x22, [sp], #16
    ldp     x23, x24, [sp], #16
    ldp     x25, x26, [sp], #16
    ldp     x27, x28, [sp], #16
    ldp     x29, x30, [sp], #16
    eret
.endm

.section .text
.align 11  /* 2KB alignment for vector table */
.globl vectors
vectors:
    /* Current EL with SP0: Synchronous */
    .align 7
    b    do_sync_exception
    /* IRQ */
    .align 7
    b    do_IRQ
    /* FIQ */
    .align 7
    b    do_FIQ
    /* SError */
    .align 7
    b    do_SError

    /* Current EL with SPx: Synchronous */
    .align 7
    b    do_sync_exception
    /* IRQ */
    .align 7
    b    do_IRQ
    /* FIQ */
    .align 7
    b    do_FIQ
    /* SError */
    .align 7
    b    do_SError

    /* Lower EL using AArch64: Synchronous (from EL1/EL0) */
    .align 7
    b    do_sync_exception_from_guest
    /* IRQ */
    .align 7
    b    do_IRQ_from_guest
    /* FIQ */
    .align 7
    b    do_FIQ_from_guest
    /* SError */
    .align 7
    b    do_SError_from_guest

    /* Lower EL using AArch64: Synchronous (from EL1/EL0, cont.) - repeated for full table */
    .align 7
    b    do_sync_exception_from_guest
    /* IRQ */
    .align 7
    b    do_IRQ_from_guest
    /* FIQ */
    .align 7
    b    do_FIQ_from_guest
    /* SError */
    .align 7
    b    do_SError_from_guest

    /* Lower EL using AArch32: Not supported in Xen ARM64 hypervisor; trap or ignore */
    .space  0x200  /* Placeholder for AArch32 vectors if needed */

/* IRQ handler for hypervisor-level interrupts (physical IRQs vectored by GICv3) */
ENTRY(do_IRQ)
    save_all
    /* Acknowledge interrupt: Read INTID from GICv3 CPU interface (EL2 view) */
    /* ARM-specific: Use dsb for memory barrier before/after GIC access */
    dsb     sy
    mrs     x0, ICC_IAR1_EL1        // Get interrupt ID (INTID)
    dsb     sy
    /* Vector based on INTID; for now, call C handler (preserve x86 logic of dispatch) */
    /* In Xen, this would check if physical or virtual, handle PPI/SPI, etc. */
    mov     x1, sp                  // Pass saved state ptr
    bl      do_IRQ_c_handler        // C function: handles INTID, EOI via ICC_EOIR1_EL1
    restore_all
ENDPROC(do_IRQ)

/* Simplified sync exception handler (e.g., for traps, faults) */
ENTRY(do_sync_exception)
    save_all
    mov     x0, sp
    bl      do_sync_exception_c
    restore_all
ENDPROC(do_sync_exception)

/* Guest entry points (from lower EL) - similar but switch to guest context */
ENTRY(do_IRQ_from_guest)
    save_all
    /* For guest IRQs: Check if virtualized; use GICv3 VGIC for vectoring */
    /* ARM-specific: Read HCR_EL2 for guest state, potentially inject vIRQ */
    mrs     x4, hcr_el2             // Hypervisor config register
    mov     x0, sp
    bl      do_IRQ_from_guest_c
    restore_all
ENDPROC(do_IRQ_from_guest)

/* Other handlers (FIQ, SError) - stubs for now, expand as per x86 equivalents */
ENTRY(do_FIQ)
    save_all
    mov     x0, sp
    bl      do_FIQ_c
    restore_all
ENDPROC(do_FIQ)

ENTRY(do_SError)
    save_all
    mov     x0, sp
    bl      do_SError_c
    restore_all
ENDPROC(do_SError)

/* Guest stubs */
ENTRY(do_sync_exception_from_guest)
ENTRY(do_FIQ_from_guest)
ENTRY(do_SError_from_guest)
    /* Similar to above; call respective C handlers for guest context */
    b    .   /* Trap for now */
ENDPROC(do_sync_exception_from_guest)
ENDPROC(do_FIQ_from_guest)
ENDPROC(do_SError_from_guest)

/* Set VBAR_EL2 in init code (not shown): msr vbar_el2, #vectors */
