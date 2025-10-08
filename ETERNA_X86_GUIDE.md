# ETERNA ARM64 → x86_64 Port Guide

## 🎯 Mission
Port CHAIN-ARM-HYPERVISOR-ETERNA (80k lines Rust ARM hypervisor) to x86_64 **in pure Rust**.

## 🦀 Rust Requirements

### Dependencies
```toml
[dependencies]
# Core x86 support
x86_64 = "0.14"       # Page tables, segmentation, etc.
raw-cpuid = "11.0"    # CPUID intrinsics
bitflags = "2.4"      # Control register flags

# VMX support (custom or vendored)
# vmx = { path = "../vmx" }  # If we build our own

[features]
default = []
std = []  # ETERNA is no_std
vmx = []  # Enable Intel VMX
```

### Key Rust Patterns

#### 1. System Register Access (ARM → x86)
**ARM64:**
```rust
// Read HCR_EL2
let hcr: u64;
unsafe { asm!("mrs {}, HCR_EL2", out(reg) hcr) }

// Write HCR_EL2
unsafe { asm!("msr HCR_EL2, {}", in(reg) value) }
```

**x86_64:**
```rust
use core::arch::x86_64::{__rdmsr, __wrmsr};

// Read VMCS field
fn vmread(field: u64) -> u64 {
    let value: u64;
    unsafe {
        asm!(
            "vmread {}, {}",
            out(reg) value,
            in(reg) field,
            options(nostack, preserves_flags)
        )
    }
    value
}

// Write VMCS field
fn vmwrite(field: u64, value: u64) {
    unsafe {
        asm!(
            "vmwrite {}, {}",
            in(reg) field,
            in(reg) value,
            options(nostack, preserves_flags)
        )
    }
}

// MSR access (APIC, etc.)
fn read_msr(msr: u32) -> u64 {
    unsafe { __rdmsr(msr) }
}

fn write_msr(msr: u32, value: u64) {
    unsafe { __wrmsr(msr, value) }
}
```

#### 2. Page Table Management (Stage-2 → EPT)
**ARM64 Stage-2:**
```rust
pub struct Stage2PageTable {
    root: PhysAddr,
    // 4-level: 512GB → 1GB → 2MB → 4KB
}

impl Stage2PageTable {
    fn map_ipa_to_pa(&mut self, ipa: u64, pa: u64, flags: u64) {
        // Walk TTBR0_EL2-based tables
    }
}
```

**x86_64 EPT:**
```rust
use x86_64::structures::paging::PageTable;

pub struct EptPageTable {
    pml4: PhysAddr,  // 4-level: PML4 → PDPT → PD → PT
}

impl EptPageTable {
    fn map_gpa_to_hpa(&mut self, gpa: u64, hpa: u64, flags: EptFlags) {
        // Walk EPT with memory types (WB, UC, etc.)
        // Set flags: Read, Write, Execute
    }
}

// EPT entry flags
bitflags! {
    pub struct EptFlags: u64 {
        const READ = 1 << 0;
        const WRITE = 1 << 1;
        const EXECUTE = 1 << 2;
        const MEMORY_TYPE_WB = 6 << 3;  // Write-back
        const IGNORE_PAT = 1 << 6;
    }
}
```

#### 3. VCPU State (ARM → x86)
**ARM64 VCPU:**
```rust
#[repr(C)]
pub struct VcpuState {
    // General-purpose
    pub x: [u64; 31],
    pub pc: u64,
    pub sp_el0: u64,
    pub sp_el1: u64,
    
    // System registers
    pub elr_el1: u64,
    pub spsr_el1: u64,
    pub sctlr_el1: u64,
    pub ttbr0_el1: u64,
    pub ttbr1_el1: u64,
    
    // FP/SIMD
    pub v: [u128; 32],
    pub fpsr: u32,
    pub fpcr: u32,
}
```

**x86_64 VCPU:**
```rust
#[repr(C)]
pub struct VcpuState {
    // General-purpose
    pub rax: u64, pub rbx: u64, pub rcx: u64, pub rdx: u64,
    pub rsi: u64, pub rdi: u64, pub rbp: u64, pub rsp: u64,
    pub r8: u64,  pub r9: u64,  pub r10: u64, pub r11: u64,
    pub r12: u64, pub r13: u64, pub r14: u64, pub r15: u64,
    pub rip: u64, pub rflags: u64,
    
    // Segment registers
    pub cs: SegmentRegister,
    pub ss: SegmentRegister,
    pub ds: SegmentRegister,
    // ... ES, FS, GS, LDTR, TR
    
    // Control registers (stored in VMCS)
    pub cr0: u64,
    pub cr3: u64,
    pub cr4: u64,
    pub efer: u64,  // MSR 0xC0000080
    
    // FPU/SSE state (XSAVE area)
    pub xsave_area: [u8; 4096],
}

#[repr(C)]
pub struct SegmentRegister {
    pub selector: u16,
    pub base: u64,
    pub limit: u32,
    pub access_rights: u32,
}
```

#### 4. Exception Handling (ARM → x86)
**ARM64 Exception Vectors:**
```rust
#[naked]
unsafe extern "C" fn exception_vectors() {
    asm!(
        ".align 11",  // 2KB alignment
        "b sync_el1t",
        ".align 7",   // 128-byte per vector
        "b irq_el1t",
        // ... 16 vectors total
        options(noreturn)
    )
}
```

**x86_64 VM-Exit Handler:**
```rust
pub fn handle_vmexit(vcpu: &mut Vcpu) -> Result<(), VmError> {
    let exit_reason = vmread(VMCS_EXIT_REASON);
    
    match exit_reason & 0xFFFF {
        EXIT_REASON_EXCEPTION_NMI => handle_exception(vcpu),
        EXIT_REASON_EXTERNAL_INTERRUPT => handle_interrupt(vcpu),
        EXIT_REASON_TRIPLE_FAULT => Err(VmError::TripleFault),
        EXIT_REASON_EPT_VIOLATION => handle_ept_fault(vcpu),
        EXIT_REASON_EPT_MISCONFIG => handle_ept_misconfig(vcpu),
        EXIT_REASON_VMCALL => handle_hypercall(vcpu),
        EXIT_REASON_CR_ACCESS => handle_cr_access(vcpu),
        EXIT_REASON_MSR_READ => handle_msr_read(vcpu),
        EXIT_REASON_MSR_WRITE => handle_msr_write(vcpu),
        _ => Err(VmError::UnknownExit(exit_reason)),
    }
}

// EPT violation (like ARM Stage-2 fault)
fn handle_ept_fault(vcpu: &mut Vcpu) -> Result<(), VmError> {
    let gpa = vmread(VMCS_GUEST_PHYSICAL_ADDRESS);
    let qualification = vmread(VMCS_EXIT_QUALIFICATION);
    
    let is_read = qualification & (1 << 0) != 0;
    let is_write = qualification & (1 << 1) != 0;
    let is_exec = qualification & (1 << 2) != 0;
    
    // Map page in EPT
    vcpu.vm.ept.map_gpa_to_hpa(gpa, alloc_page(), EptFlags::READ | EptFlags::WRITE)?;
    
    Ok(())
}
```

#### 5. Interrupt Controller (GICv3 → APIC)
**ARM64 GICv3:**
```rust
pub struct GicV3 {
    gicd_base: usize,  // Distributor
    gicr_base: usize,  // Redistributor
}

impl GicV3 {
    fn inject_irq(&mut self, vcpu: &mut Vcpu, irq: u32) {
        // Use ICH_LR registers (list registers)
        unsafe {
            asm!("msr ICH_LR0_EL2, {}", in(reg) (irq | (1 << 28)));
        }
    }
}
```

**x86_64 APIC:**
```rust
pub struct Apic {
    base: u64,  // MSR IA32_APIC_BASE
}

impl Apic {
    fn inject_irq(&mut self, vcpu: &mut Vcpu, vector: u8) {
        // Write to VMCS for virtual interrupt injection
        let mut interrupt_info = (vector as u64) & 0xFF;
        interrupt_info |= (0 << 8);  // External interrupt
        interrupt_info |= (1 << 31); // Valid
        
        vmwrite(VMCS_VM_ENTRY_INTR_INFO, interrupt_info);
        vmwrite(VMCS_VM_ENTRY_CONTROLS, 
                vmread(VMCS_VM_ENTRY_CONTROLS) | (1 << 0)); // Interrupt on entry
    }
    
    fn eoi(&self, vector: u8) {
        // Write to EOI MSR or MMIO
        write_msr(IA32_APIC_EOI, 0);
    }
}

const IA32_APIC_BASE: u32 = 0x1B;
const IA32_APIC_EOI: u32 = 0x80B;
```

## 🔧 VMX-Specific Operations

### VMXON (Enter VMX operation)
```rust
pub fn vmxon(vmxon_region: PhysAddr) -> Result<(), VmxError> {
    // Check CPUID for VMX support
    let cpuid = raw_cpuid::CpuId::new();
    if !cpuid.get_feature_info().unwrap().has_vmx() {
        return Err(VmxError::NotSupported);
    }
    
    // Enable VMX in CR4
    let mut cr4: u64;
    unsafe {
        asm!("mov {}, cr4", out(reg) cr4);
        cr4 |= 1 << 13;  // CR4.VMXE
        asm!("mov cr4, {}", in(reg) cr4);
    }
    
    // Set lock bit in IA32_FEATURE_CONTROL MSR
    let feat_ctrl = read_msr(IA32_FEATURE_CONTROL);
    write_msr(IA32_FEATURE_CONTROL, feat_ctrl | (1 << 0) | (1 << 2));
    
    // Execute VMXON
    let result: u8;
    unsafe {
        asm!(
            "vmxon [{}]",
            "setbe al",
            in(reg) &vmxon_region,
            out("al") result,
            options(nostack)
        );
    }
    
    if result != 0 {
        return Err(VmxError::VmxonFailed);
    }
    
    Ok(())
}

const IA32_FEATURE_CONTROL: u32 = 0x3A;
```

### VMCS Setup
```rust
pub fn setup_vmcs(vcpu: &Vcpu) -> Result<(), VmxError> {
    // Clear VMCS
    vmclear(vcpu.vmcs_pa)?;
    
    // Load VMCS
    vmptrld(vcpu.vmcs_pa)?;
    
    // Host state (hypervisor)
    vmwrite(VMCS_HOST_CR0, read_cr0());
    vmwrite(VMCS_HOST_CR3, read_cr3());
    vmwrite(VMCS_HOST_CR4, read_cr4());
    vmwrite(VMCS_HOST_RIP, vm_exit_handler as u64);
    vmwrite(VMCS_HOST_RSP, vcpu.host_stack_top);
    
    // Guest state (VM)
    vmwrite(VMCS_GUEST_CR0, vcpu.state.cr0);
    vmwrite(VMCS_GUEST_CR3, vcpu.state.cr3);
    vmwrite(VMCS_GUEST_CR4, vcpu.state.cr4);
    vmwrite(VMCS_GUEST_RIP, vcpu.state.rip);
    vmwrite(VMCS_GUEST_RSP, vcpu.state.rsp);
    vmwrite(VMCS_GUEST_RFLAGS, vcpu.state.rflags);
    
    // EPT pointer
    let ept_ptr = vcpu.ept.pml4 | (3 << 3) | (6 << 0);  // 4-level, WB
    vmwrite(VMCS_EPT_POINTER, ept_ptr);
    
    // Controls
    setup_execution_controls()?;
    setup_exit_controls()?;
    setup_entry_controls()?;
    
    Ok(())
}
```

## 📊 Architecture Comparison Table

| Component | ARM64 | x86_64 | Rust Crate |
|-----------|-------|--------|------------|
| **Privilege** | EL2 | VMX root | - |
| **Page Tables** | Stage-2 (TTBR) | EPT | `x86_64::structures::paging` |
| **Interrupts** | GICv3 | APIC | Custom |
| **Timers** | Generic Timer | TSC/APIC | `raw-cpuid` |
| **System Regs** | MRS/MSR | RDMSR/WRMSR | `core::arch::x86_64` |
| **VM Control** | HCR_EL2 | VMCS | Custom VMX |
| **Faults** | ESR_EL2/HPFAR | Exit reason/GPA | - |

## 🚀 Getting Started

1. **Analyze component:**
   ```bash
   curl http://localhost:8000/eterna/analyze/src/cpu/vcpu.rs
   ```

2. **Port single file:**
   ```bash
   curl -X POST http://localhost:8000/eterna/port \
     -H "Content-Type: application/json" \
     -d '{
       "file_path": "src/cpu/vcpu.rs",
       "description": "Port VCPU state to x86 VMX",
       "conversation_id": "eterna-x86-vcpu"
     }'
   ```

3. **Bulk port:**
   ```bash
   curl -X POST http://localhost:8000/eterna/port/bulk \
     -H "Content-Type: application/json" \
     -d '{
       "components": [
         "src/cpu/vcpu.rs",
         "src/memory/stage2.rs",
         "src/devices/gic/mod.rs"
       ],
       "conversation_id": "eterna-x86-bulk"
     }'
   ```

## 🎯 Port Priority

### Phase 1: Core (HIGH)
- [ ] `src/cpu/vcpu.rs` - VCPU state management
- [ ] `src/cpu/exceptions.rs` - VM-exit handling
- [ ] `src/memory/stage2.rs` - EPT implementation
- [ ] `src/boot.S` - VMX initialization

### Phase 2: Devices (MEDIUM)
- [ ] `src/devices/gic/` - APIC emulation
- [ ] `src/devices/timer/` - TSC/APIC timer
- [ ] `src/devices/uart/` - Serial port (keep same)

### Phase 3: Advanced (LOW)
- [ ] `src/cpu/numa.rs` - NUMA with SRAT
- [ ] `src/migration/` - Live migration
- [ ] `src/debug/` - GDB stub

---

**Ready to port 80k lines of Rust hypervisor!** 🦀🔥
