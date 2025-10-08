"""
ETERNA Port Agent - ARM64 → x86_64 Hypervisor Porting Specialist
Ports CHAIN-ARM-HYPERVISOR-ETERNA to x86 architecture
"""
import os
from typing import Dict, Any, List
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.openrouter_client import get_openrouter_client

class EternaPortAgent:
    """
    Specialized agent for porting ETERNA hypervisor ARM64 → x86
    - Reads Rust ARM hypervisor code
    - Generates x86 equivalents
    - Outputs to Code Window with syntax highlighting
    - Uses AI Planner for complex task breakdown
    """
    
    def __init__(self):
        self.client = get_openrouter_client()
        self.model = "x-ai/grok-4-fast"
        self.eterna_path = "/Users/matto/Documents/AI CHAT/my-app/hyper/CHAIN-ARM-HYPERVISOR-ETERNA-main"
        
        # System prompt for ARM→x86 porting
        self.system_prompt = """You are an Expert Rust Hypervisor Architect specializing in ARM64→x86 porting.

Your mission: Port CHAIN-ARM-HYPERVISOR-ETERNA (80k lines Rust ARM hypervisor) to x86_64 IN PURE RUST.

Key Architecture Mappings (ARM64 → x86_64):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIVILEGE LEVELS:
- EL2 (Hypervisor Exception Level) → VMX root mode (Ring 0 + VMX ON)
- EL1 (Kernel) → VMX non-root Ring 0
- EL0 (User) → VMX non-root Ring 3

MEMORY MANAGEMENT:
- Stage-2 translation → EPT (Extended Page Tables)
- TTBR0_EL1/TTBR1_EL1 → CR3 (guest page tables)
- TCR_EL2 → EPT pointer + controls
- MAIR_EL2 → PAT (Page Attribute Table)

INTERRUPTS:
- GICv3 (Distributor/Redistributor) → APIC + IO-APIC
- ICC_* system registers → MSR-based APIC access (0x800-0x8FF)
- IRQ/FIQ → INTR/NMI

CONTROL REGISTERS:
- HCR_EL2 → VMCS execution controls (VM_ENTRY_CONTROLS, VM_EXIT_CONTROLS)
- SCTLR_EL2 → CR0, CR4, EFER
- VBAR_EL2 → IDT base (IDTR)

EXCEPTION HANDLING:
- ESR_EL2 (Exception Syndrome) → VM-exit reason + qualification
- HPFAR_EL2 (IPA fault address) → GUEST_PHYSICAL_ADDRESS (VMCS field)
- FAR_EL2 → CR2 (page fault address)

TIMERS:
- Generic Timers (CNTPCT_EL0) → TSC (RDTSC)
- CNTP_CTL_EL0 → APIC timer control
- Timer interrupts → IRQ 0 (PIT) or APIC timer

SYSTEM CONFIG:
- PSCI (Power State) → ACPI + APICv
- Device Tree → ACPI tables (MADT, SRAT, etc.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RUST CODE REQUIREMENTS:
✅ Pure Rust with #![no_std]
✅ Use `core::arch::x86_64::*` for intrinsics (RDMSR, WRMSR, CPUID)
✅ Inline assembly with `asm!()` macro (Intel syntax preferred)
✅ x86 crates: x86_64, raw-cpuid, vmx (if needed)
✅ Safe abstractions over unsafe VMX/MSR operations
✅ Maintain ETERNA's safety invariants
✅ Comment all architecture-specific changes
✅ Use bitflags for control registers
✅ Preserve error handling (Result<T, E>)

INLINE ASSEMBLY EXAMPLES:
```rust
// ARM64 equivalent
unsafe { asm!("msr HCR_EL2, {}", in(reg) value) }

// x86 equivalent (VMX-specific)
unsafe { 
    asm!(
        "vmwrite rax, rbx",
        in("rax") vmcs_field,
        in("rbx") value,
        options(nostack, preserves_flags)
    )
}
```

OUTPUT FORMAT:
1. Brief architecture analysis (3-5 lines)
2. Complete Rust code with x86 specifics
3. Inline assembly blocks with Intel syntax
4. Comments explaining complex x86 behavior
5. Any required Cargo.toml dependencies
"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ARM→x86 porting task
        
        Args:
            task: {
                'id': str,
                'conversation_id': str,
                'description': str (e.g., "Port src/cpu/vcpu.rs to x86"),
                'file_path': str (path in ETERNA repo),
                'target': 'code_window' | 'planner' | 'both'
            }
        
        Returns:
            {
                'task_id': str,
                'output': {
                    'code': str (Rust x86 port),
                    'analysis': str (architecture notes),
                    'plan': List[str] (sub-tasks if complex)
                },
                'status': 'completed' | 'failed',
                'ui_target': 'code_window' | 'planner'
            }
        """
        try:
            # 1. Read ARM source file
            source_path = os.path.join(self.eterna_path, task['file_path'])
            if os.path.exists(source_path):
                with open(source_path, 'r') as f:
                    arm_code = f.read()
            else:
                arm_code = f"File not found: {source_path}"
            
            # 2. Determine if task needs planning breakdown
            needs_planning = self._needs_complex_planning(task['description'], arm_code)
            
            # 3. Build prompt
            user_prompt = f"""
Task: {task['description']}
ARM Source File: {task['file_path']}
Lines of Code: {len(arm_code.split(chr(10)))}

ARM64 Code:
```rust
{arm_code[:15000]}  # Truncate for token limits
```

Requirements:
1. Port this ARM64 hypervisor code to x86_64
2. Maintain Rust safety (no_std compatible)
3. Use x86 architecture equivalents
4. Add inline assembly where needed (use `asm!` macro)
5. Comment complex architecture changes

{"IMPORTANT: This is a complex task. First output a breakdown plan with 5-10 sub-tasks." if needs_planning else ""}

Generate:
1. Architecture analysis (ARM vs x86 differences)
2. Complete x86 Rust port
3. {"Task breakdown for AI Planner" if needs_planning else "Summary"}
"""
            
            # 4. Call Grok
            response = await self.client.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                max_tokens=16384,  # Large for complete ports
                temperature=0.2  # Precise architecture work
            )
            
            output = response.choices[0].message.content
            
            # 5. Parse output for UI targets
            code, analysis, plan = self._parse_output(output, needs_planning)
            
            return {
                "task_id": task['id'],
                "output": {
                    "code": code,
                    "analysis": analysis,
                    "plan": plan
                },
                "status": "completed",
                "ui_target": "both" if needs_planning else "code_window",
                "file_path": task['file_path'].replace('src/', 'x86_port/src/')
            }
            
        except Exception as e:
            print(f"❌ ETERNA Port Agent error: {e}")
            return {
                "task_id": task['id'],
                "output": {"error": str(e)},
                "status": "failed"
            }
    
    def _needs_complex_planning(self, description: str, code: str) -> bool:
        """Determine if task needs AI Planner breakdown"""
        # Complex if:
        # - Large file (>500 lines)
        # - Multiple architecture components
        # - Assembly-heavy
        lines = len(code.split('\n'))
        
        complex_keywords = [
            'vcpu', 'exception', 'mmu', 'stage2', 'interrupt',
            'gic', 'timer', 'device', 'boot', 'page_fault'
        ]
        
        has_complex = any(kw in description.lower() for kw in complex_keywords)
        
        return lines > 500 or has_complex
    
    def _parse_output(self, output: str, needs_planning: bool) -> tuple:
        """Parse Grok output into code, analysis, plan"""
        # Simple heuristic parsing
        sections = output.split('```')
        
        code = ""
        analysis = ""
        plan = []
        
        # Extract code blocks
        for i, section in enumerate(sections):
            if i % 2 == 1:  # Odd indices are code blocks
                if 'rust' in sections[i-1].lower() or 'asm' in sections[i-1].lower():
                    code += section + "\n\n"
        
        # Extract analysis (usually before first code block)
        if len(sections) > 0:
            analysis = sections[0]
        
        # Extract plan if needed
        if needs_planning:
            plan_lines = [line.strip() for line in output.split('\n') 
                         if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-'))]
            plan = plan_lines[:10]  # Max 10 items
        
        return code, analysis, plan


async def route_to_ui(port_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route agent output to appropriate UI components
    
    Returns structure for frontend:
    {
        'code_window': {...},  # For Code Canvas
        'planner': {...},       # For AI Planner
        'status': {...}         # For status panel
    }
    """
    ui_response = {
        'code_window': None,
        'planner': None,
        'status': {
            'task_id': port_result['task_id'],
            'status': port_result['status'],
            'timestamp': 'now'
        }
    }
    
    if port_result['status'] == 'completed':
        # Send to Code Window
        ui_response['code_window'] = {
            'file_path': port_result.get('file_path', 'untitled.rs'),
            'language': 'rust',
            'content': port_result['output']['code'],
            'analysis': port_result['output']['analysis'],
            'tab_label': f"x86: {port_result.get('file_path', 'port').split('/')[-1]}"
        }
        
        # Send to Planner if complex
        if port_result.get('ui_target') in ['planner', 'both']:
            ui_response['planner'] = {
                'task_name': f"Port {port_result.get('file_path', 'component')}",
                'subtasks': port_result['output']['plan'],
                'parent_id': port_result['task_id'],
                'status': 'in_progress'
            }
    
    return ui_response
