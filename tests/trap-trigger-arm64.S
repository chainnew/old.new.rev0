/*
 * ARM64 test code to systematically trigger migrated trap handlers in Xen hypervisor.
 * This assembly file executes sequences that provoke common synchronous exceptions
 * (traps) on ARM64, such as undefined instructions, aborts (page faults), and SVC calls.
 * Intended to run in a guest context (e.g., DomU at EL0) to trap into the hypervisor (EL2).
 * Each test is labeled and uses a simple branch structure; traps will interrupt execution.
 * For testing: Compile with aarch64-elf-gcc, link, and run under Xen with debug hooks.
 * Assumptions: Standard Xen ARM64 trap dispatch for exceptions like ESR_ELx codes.
 * No async exceptions (IRQs) triggered here; focus on synchronous traps.
 */

.section .text
.global _start

_start:
    /* Initialize minimal stack pointer (assume provided by loader) */
    mov sp, #0x80000  /* Example stack top; adjust as needed */

    /* Test 1: Trigger Undefined Instruction Trap (ESR: ILL) */
    /* Use UDF (Undefined Instruction) to provoke an undefined instr exception. */
test_undef:
    adr x0, test_undef_msg
    /* In real test, print or log; here just trigger */
    udf #0x1234  /* Undefined instruction; traps to hypervisor with ESR ILL_ILL */
    b test_svc    /* Won't reach if trap handled correctly */

test_undef_msg:
    .asciz "Triggering Undefined Instruction Trap\n"

    .align 4

    /* Test 2: Trigger Supervisor Call (SVC) Trap (ESR: SVC) */
    /* SVC is used for hypercalls in Xen ARM; this mimics a guest hypercall. */
test_svc:
    adr x0, test_svc_msg
    mov x1, #42    /* Example arg */
    svc #0         /* Supervisor Call; traps to EL2 with ESR SVC64 */
    b test_data_abort  /* Fallback if not trapped */

test_svc_msg:
    .asciz "Triggering SVC (Hypercall) Trap\n"

    .align 4

    /* Test 3: Trigger Data Abort (Page Fault) on Load (ESR: DABT) */
    /* Access unmapped memory to cause translation fault (page fault equivalent). */
test_data_abort:
    adr x0, test_data_abort_msg
    /* Assume 0xdeadbeef00000000 is an invalid guest virtual address */
    ldr x2, =0xdeadbeef00000000  /* Invalid VA */
    ldr x1, [x2]                  /* Load from invalid addr; data abort (trans fault) */
    b test_instr_abort           /* Won't reach */

test_data_abort_msg:
    .asciz "Triggering Data Abort (Page Fault) Trap\n"

    .align 4

    /* Test 4: Trigger Instruction Abort (Page Fault) on Fetch (ESR: IABT) */
    /* Jump to unmapped code area to cause instruction fetch abort. */
test_instr_abort:
    adr x0, test_instr_abort_msg
    ldr x3, =0xdeadbeef00001000  /* Invalid code VA */
    br x3                         /* Branch to invalid addr; instr abort (trans fault) */
    /* Note: This may not execute the branch if addr is invalid, but provokes IABT */

test_instr_abort_msg:
    .asciz "Triggering Instruction Abort Trap\n"

    .align 4

    /* Test 5: Trigger Alignment Fault (if enabled; ESR: DABT ALIGN) */
    /* Misaligned load/store; assumes strict alignment checking (SCTLR.A=1). */
test_align_fault:
    adr x0, test_align_msg
    mov x4, #1                    /* Odd address for misalignment */
    str x4, [x4]                  /* Store to misaligned addr; alignment fault if enabled */
    b test_fp_trap               /* Fallback */

test_align_msg:
    .asciz "Triggering Alignment Fault Trap\n"

    .align 4

    /* Test 6: Trigger FP Trap (if FP disabled; ESR: FP) */
    /* Attempt FP operation when FP not enabled (CPACR.FPEN=0). */
test_fp_trap:
    adr x0, test_fp_msg
    fmov d0, #1.0                 /* FP move; traps if FP disabled in guest */
    fadd d1, d0, d0               /* FP add to provoke */
    b _end

test_fp_msg:
    .asciz "Triggering FP Trap (if disabled)\n"

    .align 4

_end:
    /* Infinite loop if no trap */
    b _end

    /* Data section for messages (if logging) */
.section .rodata
    .align 3
