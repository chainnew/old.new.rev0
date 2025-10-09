"""
Hypervisor Port Orchestrator - Tie Agents to Rust Builds
Orchestrates ETERNA x86 porting with agent-driven code generation + cargo validation
"""
import asyncio
import os
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from agents.primary_agent import PrimaryAgent
from agents.code_agent import CodeAgent
from agents.eterna_port_agent import EternaPortAgent, route_to_ui
from agents.swarm_coordinator import SwarmCoordinator, get_coordinator


class HypervisorPortOrchestrator:
    """
    End-to-end orchestration for ETERNA ARM64 → x86_64 porting
    
    Workflow:
    1. PrimaryAgent decomposes port task
    2. CodeAgent/EternaPortAgent generate Rust code
    3. Save to x86_port/src/
    4. Run `cargo check` for validation
    5. Optional: Build and run in QEMU
    """
    
    def __init__(self, x86_port_path: str = None):
        # Agents
        self.primary = PrimaryAgent()
        self.code_agent = CodeAgent()
        self.eterna_agent = EternaPortAgent()
        
        # Swarm coordinator
        self.coordinator = get_coordinator()
        
        # Register agents
        self.agents = {
            'primary': self.primary,
            'code': self.code_agent,
            'eterna_port': self.eterna_agent
        }
        
        # x86_port directory
        if x86_port_path:
            self.x86_port_path = Path(x86_port_path)
        else:
            # Auto-detect from ETERNA location
            eterna_path = Path("/Users/matto/Documents/AI CHAT/my-app/hyper/CHAIN-ARM-HYPERVISOR-ETERNA-main")
            self.x86_port_path = eterna_path / "x86_port"
        
        # Stats
        self.stats = {
            'files_generated': 0,
            'cargo_checks': 0,
            'cargo_failures': 0,
            'build_attempts': 0
        }
        
        print(f"🚀 HypervisorPortOrchestrator initialized")
        print(f"📁 x86_port path: {self.x86_port_path}")
    
    async def port_hypervisor(
        self, 
        task_description: str, 
        conversation_id: str,
        validate_rust: bool = True,
        build: bool = False
    ) -> Dict[str, Any]:
        """
        Port ETERNA hypervisor component(s)
        
        Args:
            task_description: High-level porting task (e.g., "Port full VMCS to x86")
            conversation_id: Conversation UUID
            validate_rust: Run cargo check on generated code
            build: Attempt full cargo build
            
        Returns:
            Orchestration results with code, validation, build status
        """
        print(f"\n{'='*60}")
        print(f"🔥 HYPERVISOR PORT ORCHESTRATION")
        print(f"{'='*60}")
        print(f"Task: {task_description}")
        print(f"Conversation: {conversation_id}")
        print(f"{'='*60}\n")
        
        start_time = datetime.now()
        results = {
            'task': task_description,
            'conversation_id': conversation_id,
            'subtasks': [],
            'generated_files': [],
            'validation': {},
            'build': {},
            'status': 'in_progress'
        }
        
        # Step 1: Primary agent decomposes task
        print("📋 Step 1: Decomposing task...")
        subtasks = await self.primary.decompose(task_description, conversation_id)
        results['subtasks'] = subtasks
        print(f"✅ Decomposed into {len(subtasks)} subtasks\n")
        
        # Step 2: Route to specialist agents (parallel execution)
        print("🤖 Step 2: Executing specialist agents...")
        agent_coroutines = []
        
        for task in subtasks:
            # Route to appropriate agent
            task_type = task.get('type', 'code')
            
            if task_type == 'port' or 'eterna' in task.get('description', '').lower():
                # Use EternaPortAgent for hypervisor-specific porting
                agent_coroutines.append(self.eterna_agent.execute(task))
            else:
                # Use CodeAgent for general code migration
                agent_coroutines.append(self.code_agent.execute(task))
        
        # Execute all in parallel
        agent_results = await asyncio.gather(*agent_coroutines, return_exceptions=True)
        
        # Process results
        generated_files = []
        for i, result in enumerate(agent_results):
            if isinstance(result, Exception):
                print(f"❌ Subtask {i} failed: {result}")
                results['subtasks'][i]['status'] = 'failed'
            else:
                print(f"✅ Subtask {i} completed")
                
                # Save generated code to x86_port
                if result.get('status') == 'completed' and 'output' in result:
                    file_path = result.get('file_path', f'generated_{i}.rs')
                    code = result['output'].get('code', '')
                    
                    if code:
                        saved_path = await self._save_rust_file(file_path, code)
                        if saved_path:
                            generated_files.append(saved_path)
                            self.stats['files_generated'] += 1
        
        results['generated_files'] = generated_files
        print(f"\n💾 Saved {len(generated_files)} Rust files\n")
        
        # Step 3: Validate with cargo check
        if validate_rust and generated_files:
            print("🔍 Step 3: Validating Rust syntax with cargo check...")
            validation_result = await self._run_cargo_check()
            results['validation'] = validation_result
            
            if validation_result.get('success'):
                print("✅ Cargo check passed!")
            else:
                print(f"❌ Cargo check failed:\n{validation_result.get('stderr', '')[:500]}")
        
        # Step 4: Optional full build
        if build:
            print("\n🔨 Step 4: Building hypervisor...")
            build_result = await self._run_cargo_build()
            results['build'] = build_result
            
            if build_result.get('success'):
                print("✅ Build successful!")
                
                # Optional: Offer to run in QEMU
                print("\n💡 Tip: Run in QEMU with:")
                print(f"    cd {self.x86_port_path}")
                print(f"    make qemu")
            else:
                print(f"❌ Build failed:\n{build_result.get('stderr', '')[:500]}")
        
        # Step 5: Integrate results
        print("\n🔗 Step 5: Integrating results...")
        integrated_summary = await self.primary.integrate(agent_results, conversation_id)
        results['summary'] = integrated_summary
        results['status'] = 'completed'
        
        # Calculate stats
        elapsed = (datetime.now() - start_time).total_seconds()
        results['elapsed_seconds'] = elapsed
        results['stats'] = self.stats
        
        print(f"\n{'='*60}")
        print(f"✅ ORCHESTRATION COMPLETE ({elapsed:.2f}s)")
        print(f"{'='*60}")
        print(f"Files generated: {len(generated_files)}")
        print(f"Cargo checks: {self.stats['cargo_checks']}")
        print(f"{'='*60}\n")
        
        return results
    
    async def _save_rust_file(self, relative_path: str, code: str) -> Optional[str]:
        """Save generated Rust code to x86_port/src/"""
        try:
            # Determine full path
            if relative_path.startswith('x86_port/'):
                relative_path = relative_path.replace('x86_port/', '')
            
            full_path = self.x86_port_path / relative_path
            
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w') as f:
                f.write(code)
            
            print(f"💾 Saved: {full_path}")
            return str(full_path)
            
        except Exception as e:
            print(f"❌ Failed to save {relative_path}: {e}")
            return None
    
    async def _run_cargo_check(self) -> Dict[str, Any]:
        """Run cargo check to validate Rust syntax"""
        try:
            self.stats['cargo_checks'] += 1
            
            result = subprocess.run(
                ['cargo', 'check'],
                cwd=str(self.x86_port_path),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            if not success:
                self.stats['cargo_failures'] += 1
            
            return {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Cargo check timed out (>60s)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _run_cargo_build(self) -> Dict[str, Any]:
        """Run cargo build (release mode)"""
        try:
            self.stats['build_attempts'] += 1
            
            result = subprocess.run(
                ['cargo', 'build', '--release'],
                cwd=str(self.x86_port_path),
                capture_output=True,
                text=True,
                timeout=300  # 5 min
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Cargo build timed out (>5min)'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def run_qemu_test(self, iso_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run hypervisor in QEMU (non-blocking)
        
        Args:
            iso_path: Optional path to guest ISO
            
        Returns:
            QEMU process info
        """
        try:
            # Check if hypervisor binary exists
            binary_path = self.x86_port_path / "target" / "x86_64-unknown-none" / "release" / "hypervisor"
            
            if not binary_path.exists():
                return {
                    'success': False,
                    'error': 'Hypervisor binary not found. Run cargo build first.'
                }
            
            # Build QEMU command
            qemu_cmd = [
                'qemu-system-x86_64',
                '-kernel', str(binary_path),
                '-m', '2G',
                '-cpu', 'host',
                '-enable-kvm',  # Use KVM if available
                '-serial', 'stdio',
                '-nographic'
            ]
            
            if iso_path:
                qemu_cmd.extend(['-cdrom', iso_path])
            
            print(f"🖥️  Starting QEMU: {' '.join(qemu_cmd)}")
            print("💡 Press Ctrl+A then X to exit QEMU\n")
            
            # Start QEMU (non-blocking)
            process = subprocess.Popen(
                qemu_cmd,
                cwd=str(self.x86_port_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return {
                'success': True,
                'pid': process.pid,
                'command': ' '.join(qemu_cmd)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# ============================================
# CLI Interface
# ============================================

async def main():
    """Example usage"""
    import sys
    import uuid
    
    # Parse args
    if len(sys.argv) < 2:
        print("Usage: python hypervisor_port_orchestrator.py <task_description> [--build] [--qemu]")
        print("\nExamples:")
        print("  python hypervisor_port_orchestrator.py 'Port VMCS to x86'")
        print("  python hypervisor_port_orchestrator.py 'Port full VCPU management' --build")
        print("  python hypervisor_port_orchestrator.py 'Port interrupt handling' --build --qemu")
        sys.exit(1)
    
    task_description = sys.argv[1]
    build = '--build' in sys.argv
    run_qemu = '--qemu' in sys.argv
    
    conversation_id = str(uuid.uuid4())
    
    # Initialize orchestrator
    orchestrator = HypervisorPortOrchestrator()
    
    # Run port
    results = await orchestrator.port_hypervisor(
        task_description=task_description,
        conversation_id=conversation_id,
        validate_rust=True,
        build=build
    )
    
    # Optional QEMU
    if run_qemu and results.get('build', {}).get('success'):
        qemu_result = await orchestrator.run_qemu_test()
        if qemu_result.get('success'):
            print(f"\n🖥️  QEMU running (PID: {qemu_result['pid']})")
        else:
            print(f"\n❌ QEMU failed: {qemu_result.get('error')}")
    
    # Print final summary
    print(f"\n📊 Final Summary:")
    print(f"   Status: {results['status']}")
    print(f"   Files: {len(results['generated_files'])}")
    print(f"   Time: {results['elapsed_seconds']:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
