/*
 * QEMU Test Harness for Xen ARM64 Trap Handlers
 *
 * This program serves as a guest user-space test to systematically trigger
 * common ARM64 synchronous exceptions (traps) that would be handled by the
 * Xen hypervisor in a paravirtualized or hardware virtualized guest context.
 * It installs signal handlers to catch and log the exceptions, skipping the
 * faulting instruction to allow continuation.
 *
 * To use:
 * 1. Compile for ARM64: gcc -o qemu-trap-test tools/qemu-trap-test.c
 * 2. Build Xen ARM64 image and a minimal domU (e.g., Linux ARM64) including this binary.
 * 3. Boot Xen in QEMU with: qemu-system-aarch64 -M virt -cpu cortex-a57 -smp 1 -m 512M -kernel xen.gz -initrd domU-initrd.img -serial stdio -nographic
 *    (Adjust paths; ensure domU starts this test binary, e.g., via init script.)
 * 4. Observe serial output for logs. Success if expected signals are caught and skipped without crash.
 *
 * Tests focus on migrated trap equivalents:
 * - Data Abort (x86 #PF equivalent)
 * - Undefined Instruction (x86 #UD equivalent)
 * - FP Divide by Zero (x86 #DE/#XF equivalent, via FPE)
 *
 * Runs under guest OS (e.g., Linux); Xen trap handlers inject exceptions to guest.
 * If Xen handlers are broken, tests may crash or fail to catch.
 */

#include <stdio.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>
#include <fenv.h>  /* for feenableexcept */
#include <ucontext.h>  /* for ucontext_t on ARM64 */

static volatile sig_atomic_t caught_signal = 0;
static volatile sig_atomic_t fault_addr = 0;
static volatile int test_passed = 0;

void trap_signal_handler(int sig, siginfo_t *info, void *ucontext) {
    ucontext_t *uc = (ucontext_t *)ucontext;
    caught_signal = sig;
    if (info) {
        fault_addr = (uintptr_t)info->si_addr;
    }
    printf("[TRAP LOG] Caught signal %d (0x%x) at address 0x%lx\n",
           sig, sig, fault_addr);

    /* Skip the faulting instruction on ARM64 (instructions are 4 bytes).
     * On ARM64, uc_mcontext.pc points to the faulting instruction.
     * Increment by 4 to skip it, allowing continuation.
     * This tests if Xen correctly injects the exception to guest without corruption.
     */
    uc->uc_mcontext.pc += 4;
    test_passed = 1;
}

typedef struct {
    const char *name;
    void (*trigger)(void);
    int expected_sig;
} test_t;

void setup_signals(void) {
    struct sigaction sa = {0};
    sa.sa_sigaction = trap_signal_handler;
    sa.sa_flags = SA_SIGINFO | SA_RESTART;
    sigemptyset(&sa.sa_mask);

    if (sigaction(SIGSEGV, &sa, NULL) == -1 ||
        sigaction(SIGILL, &sa, NULL) == -1 ||
        sigaction(SIGFPE, &sa, NULL) == -1) {
        perror("sigaction failed");
        exit(1);
    }

    /* Enable FP divide-by-zero trap for reliable SIGFPE */
    feenableexcept(FE_DIVBYZERO);
}

void trigger_data_abort(void) {
    /* Trigger data abort (alignment or invalid access) by dereferencing NULL.
     * Equivalent to x86 #PF on invalid memory access.
     * Xen trap handler should deliver SEGV to guest.
     */
    printf("[TEST] Triggering data abort...\n");
    volatile int *ptr = (int *)0x0;
    *ptr = 42;  /* Faulting instruction: str */
    printf("Data abort skipped successfully.\n");
}

void trigger_undefined_instruction(void) {
    /* Trigger undefined instruction exception using UDF (undefined instruction).
     * Equivalent to x86 #UD.
     * On ARM64, this is a synchronous exception trapped to Xen, then injected as SIGILL.
     */
    printf("[TEST] Triggering undefined instruction...\n");
    __asm__ volatile ("udf #0");  /* 4-byte undefined instruction */
    printf("Undefined instruction skipped successfully.\n");
}

void trigger_fp_divide_by_zero(void) {
    /* Trigger FP exception via divide by zero.
     * Equivalent to x86 #DE or #XF.
     * With FE_DIVBYZERO enabled, fdiv by 0 raises SIGFPE.
     * Xen handles the synchronous FP exception.
     */
    printf("[TEST] Triggering FP divide by zero...\n");
    volatile float a = 1.0f;
    volatile float b = 0.0f;
    volatile float result = a / b;  /* Faulting instruction: fdiv */
    (void)result;
    printf("FP divide by zero skipped successfully.\n");
}

int run_test(const test_t *t) {
    caught_signal = 0;
    fault_addr = 0;
    test_passed = 0;

    t->trigger();

    if (test_passed && caught_signal == t->expected_sig) {
        printf("[RESULT] PASS: %s - Signal %d caught and skipped.\n", t->name, caught_signal);
        return 1;
    } else {
        printf("[RESULT] FAIL: %s - Expected %d, got %d (passed=%d).\n",
               t->name, t->expected_sig, caught_signal, test_passed);
        return 0;
    }
}

int main(void) {
    printf("Xen ARM64 Trap Handler Test Harness\n");
    printf("=====================================\n");
    setup_signals();

    test_t tests[] = {
        {"Data Abort (SIGSEGV)", trigger_data_abort, SIGSEGV},
        {"Undefined Instruction (SIGILL)", trigger_undefined_instruction, SIGILL},
        {"FP Divide by Zero (SIGFPE)", trigger_fp_divide_by_zero, SIGFPE},
        {NULL, NULL, 0}
    };

    int total = 0, passed = 0;
    for (int i = 0; tests[i].name; ++i) {
        total++;
        if (run_test(&tests[i])) {
            passed++;
        }
        /* Brief pause to observe output */
        usleep(100000);
    }

    printf("\nSummary: %d/%d tests passed.\n", passed, total);
    if (passed == total) {
        printf("All migrated trap handlers appear functional under Xen.\n");
        return 0;
    } else {
        return 1;
    }
}
