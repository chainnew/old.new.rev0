/*
 * Xen ARM64 Performance Benchmark Suite
 * Measures IRQ latency, timer accuracy, trap overhead
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <signal.h>
#include <sys/time.h>
#include <unistd.h>

#define ITERATIONS 10000

volatile sig_atomic_t irq_count = 0;
struct timespec start_time, end_time;

void irq_handler(int sig)
{
    irq_count++;
}

/* Benchmark IRQ latency */
void benchmark_irq_latency(void)
{
    struct sigaction sa = {0};
    sa.sa_handler = irq_handler;
    sigaction(SIGALRM, &sa, NULL);
    
    struct itimerval timer;
    timer.it_value.tv_sec = 0;
    timer.it_value.tv_usec = 100;
    timer.it_interval = timer.it_value;
    
    clock_gettime(CLOCK_MONOTONIC, &start_time);
    setitimer(ITIMER_REAL, &timer, NULL);
    
    while (irq_count < ITERATIONS) {
        pause();
    }
    
    clock_gettime(CLOCK_MONOTONIC, &end_time);
    
    double elapsed = (end_time.tv_sec - start_time.tv_sec) +
                    (end_time.tv_nsec - start_time.tv_nsec) / 1e9;
    double latency_us = (elapsed * 1e6) / ITERATIONS;
    
    printf("IRQ Latency: %.2f μs (avg over %d iterations)\n", 
           latency_us, ITERATIONS);
}

/* Benchmark timer accuracy */
void benchmark_timer_accuracy(void)
{
    struct timespec req = {.tv_sec = 0, .tv_nsec = 1000000}; // 1ms
    struct timespec start, end;
    double total_error = 0;
    
    for (int i = 0; i < 1000; i++) {
        clock_gettime(CLOCK_MONOTONIC, &start);
        nanosleep(&req, NULL);
        clock_gettime(CLOCK_MONOTONIC, &end);
        
        double actual_ns = (end.tv_sec - start.tv_sec) * 1e9 +
                          (end.tv_nsec - start.tv_nsec);
        double error_ns = actual_ns - 1000000.0;
        total_error += error_ns;
    }
    
    printf("Timer Accuracy: %.2f ns avg error\n", total_error / 1000);
}

/* Benchmark trap overhead */
void benchmark_trap_overhead(void)
{
    struct timespec start, end;
    
    clock_gettime(CLOCK_MONOTONIC, &start);
    
    for (int i = 0; i < ITERATIONS; i++) {
        asm volatile("svc #0" ::: "memory");
    }
    
    clock_gettime(CLOCK_MONOTONIC, &end);
    
    double elapsed = (end.tv_sec - start.tv_sec) +
                    (end.tv_nsec - start.tv_nsec) / 1e9;
    double overhead_ns = (elapsed * 1e9) / ITERATIONS;
    
    printf("Trap Overhead: %.2f ns per trap\n", overhead_ns);
}

int main(void)
{
    printf("=== Xen ARM64 Performance Benchmarks ===\n\n");
    
    benchmark_irq_latency();
    benchmark_timer_accuracy();
    benchmark_trap_overhead();
    
    printf("\nBenchmarks complete!\n");
    return 0;
}
