#!/usr/bin/env python3
"""
Script to clean themes.json by removing duplicates and enrich with hypervisor
porting annotations for x86 to ARM64 traps in Xen context.

Assumptions:
  - themes.json is a JSON array of objects, each with a 'theme' key (string).
  - Duplicates are identified by exact 'theme' string match (case-sensitive).
  - Enrichment adds an 'arm_annotation' field with porting notes for relevant traps.
  - Trap-related themes are pattern-matched (e.g., containing 'trap', 'exception', 'interrupt').
  - Output: super_themes_enhanced.json in the same directory as input.

Usage: python3 clean_themes.py
"""

import json
import os
import sys
from typing import Dict, List, Any

# Directory containing the input file
DB_CLEANING_DIR = "db-cleaning"
INPUT_FILE = os.path.join(DB_CLEANING_DIR, "themes.json")
OUTPUT_FILE = "super_themes_enhanced.json"

# Sample annotations for x86 to ARM64 trap porting in Xen hypervisor.
# These are architecture-specific changes for trap handling (e.g., exceptions, interrupts).
# Focus: Registers (e.g., x86 IDT vs ARM VBAR), instructions (e.g., INT vs SVC), memory model.
TRAP_ANNOTATIONS: Dict[str, str] = {
    "idt": (
        "x86: Interrupt Descriptor Table (IDT) for trap vectors.\n"
        "ARM64: Use Vector Base Address Register (VBAR_EL2) to set exception vector table.\n"
        "Port: Replace IDT loading (LIDT) with MSR VBAR_EL2; vectors at 0x800 offsets."
    ),
    "gpf": (
        "#GPF (General Protection Fault) on x86.\n"
        "ARM64: Equivalent to Data Abort or Permission faults (SError or Sync Exception).\n"
        "Port: Handle in EL2 trap handler; use ESR_EL2 for syndrome, FAR_EL2 for fault address.\n"
        "Comment: ARM's exception model is banked; preserve guest PC via ELR_EL2."
    ),
    "pagefault": (
        "x86: Page Fault (#PF) via CR2 for fault address.\n"
        "ARM64: Translation faults handled via IFAR_EL2/DFAR_EL2.\n"
        "Port: In Xen's do_trap_pagefault, map CR2 to FAR_EL2; use HSR (Hyp Syndrome) for details."
    ),
    "syscall": (
        "x86: SYSENTER/SYSCALL for fast syscalls, trapped via IDT.\n"
        "ARM64: Use HVC (Hypervisor Call) instruction for guest hypercalls.\n"
        "Port: Replace SYSCALL with HVC in guest code; trap to EL2 via VBAR vectors (offset 0x600 for HVC)."
    ),
    "nmi": (
        "x86: Non-Maskable Interrupt (NMI).\n"
        "ARM64: No direct NMI; use SError for physical errors or FIQ for async.\n"
        "Port: Emulate via pending IRQ in GIC; handle in async exception vectors."
    ),
    "default": (
        "Generic trap porting note:\n"
        "x86 traps use segment/privilege checks; ARM64 uses EL (Exception Levels).\n"
        "Preserve logic: Return to guest via ERET on ARM (vs IRET on x86).\n"
        "Memory: ARM64 is weakly ordered; add barriers (DSB/ISB) around trap entry/exit."
    )
}


def find_annotation(theme: str) -> str:
    """Find or generate annotation based on theme keywords."""
    theme_lower = theme.lower()
    for key in TRAP_ANNOTATIONS:
        if key in theme_lower:
            return TRAP_ANNOTATIONS[key]
    return TRAP_ANNOTATIONS["default"]


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    with open(INPUT_FILE, "r") as f:
        themes: List[Dict[str, Any]] = json.load(f)

    # Remove duplicates: keep unique by 'theme' key
    unique_themes = []
    seen = set()
    for item in themes:
        if isinstance(item, dict) and "theme" in item:
            th = item["theme"]
            if th not in seen:
                seen.add(th)
                # Enrich with annotation if trap-related
                if any(word in th.lower() for word in ["trap", "exception", "interrupt", "fault"]):
                    item["arm_annotation"] = find_annotation(th)
                unique_themes.append(item)
        else:
            # Fallback for non-dict items (e.g., string themes)
            theme_str = str(item)
            if theme_str not in seen:
                seen.add(theme_str)
                enriched = {"theme": item}
                if any(word in theme_str.lower() for word in ["trap", "exception", "interrupt", "fault"]):
                    enriched["arm_annotation"] = find_annotation(theme_str)
                unique_themes.append(enriched)

    # Output to file in current dir
    with open(OUTPUT_FILE, "w") as f:
        json.dump(unique_themes, f, indent=2)

    print(f"✅ Cleaned {len(themes) - len(unique_themes)} duplicates.")
    print(f"✅ Enriched {sum(1 for t in unique_themes if 'arm_annotation' in t)} themes.")
    print(f"📄 Output: {OUTPUT_FILE}")
    print(f"📊 Total unique themes: {len(unique_themes)}")


if __name__ == "__main__":
    main()
