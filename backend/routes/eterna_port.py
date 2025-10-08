"""
ETERNA Porting API Routes
Endpoints for ARM→x86 hypervisor porting with UI integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from agents.eterna_port_agent import EternaPortAgent, route_to_ui

router = APIRouter(prefix="/eterna", tags=["eterna-port"])

class PortRequest(BaseModel):
    file_path: str  # Path in ETERNA repo (e.g., "src/cpu/vcpu.rs")
    description: str  # Task description
    conversation_id: str
    target_ui: str = "both"  # 'code_window' | 'planner' | 'both'

class PortResponse(BaseModel):
    task_id: str
    status: str
    ui_data: dict

@router.post("/port", response_model=PortResponse)
async def port_component(request: PortRequest):
    """
    Port a single ETERNA component from ARM→x86
    
    Example:
    POST /eterna/port
    {
        "file_path": "src/cpu/vcpu.rs",
        "description": "Port VCPU state management to x86 VMX",
        "conversation_id": "eterna-x86-001"
    }
    """
    agent = EternaPortAgent()
    
    task = {
        'id': f"{request.conversation_id}-{request.file_path.replace('/', '-')}",
        'conversation_id': request.conversation_id,
        'description': request.description,
        'file_path': request.file_path,
        'target': request.target_ui
    }
    
    # Execute port
    result = await agent.execute(task)
    
    # Route to UI
    ui_data = await route_to_ui(result)
    
    return PortResponse(
        task_id=result['task_id'],
        status=result['status'],
        ui_data=ui_data
    )


class BulkPortRequest(BaseModel):
    components: List[str]  # List of file paths
    conversation_id: str

@router.post("/port/bulk")
async def port_bulk(request: BulkPortRequest):
    """
    Port multiple components in parallel
    
    Example:
    POST /eterna/port/bulk
    {
        "components": [
            "src/cpu/vcpu.rs",
            "src/cpu/exceptions.rs",
            "src/memory/stage2.rs"
        ],
        "conversation_id": "eterna-x86-bulk-001"
    }
    """
    agent = EternaPortAgent()
    
    tasks = [
        {
            'id': f"{request.conversation_id}-{path.replace('/', '-')}",
            'conversation_id': request.conversation_id,
            'description': f"Port {path} to x86",
            'file_path': path,
            'target': 'both'
        }
        for path in request.components
    ]
    
    # Execute in parallel
    results = await asyncio.gather(*[agent.execute(task) for task in tasks])
    
    # Route all to UI
    ui_responses = await asyncio.gather(*[route_to_ui(r) for r in results])
    
    return {
        "total": len(results),
        "completed": sum(1 for r in results if r['status'] == 'completed'),
        "failed": sum(1 for r in results if r['status'] == 'failed'),
        "ui_data": ui_responses
    }


@router.get("/analyze/{file_path:path}")
async def analyze_component(file_path: str):
    """
    Analyze ETERNA component for porting complexity
    Returns estimate of effort and sub-tasks needed
    """
    import os
    
    eterna_path = "/Users/matto/Documents/AI CHAT/my-app/hyper/CHAIN-ARM-HYPERVISOR-ETERNA-main"
    full_path = os.path.join(eterna_path, file_path)
    
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    lines = len(content.split('\n'))
    
    # Simple complexity heuristic
    complexity_score = 0
    if 'asm!' in content:
        complexity_score += 3
    if 'unsafe' in content:
        complexity_score += 2
    if lines > 500:
        complexity_score += 2
    if any(kw in content.lower() for kw in ['vcpu', 'exception', 'mmu']):
        complexity_score += 1
    
    return {
        "file_path": file_path,
        "lines": lines,
        "complexity": "high" if complexity_score >= 5 else "medium" if complexity_score >= 3 else "low",
        "estimated_time_minutes": lines / 10,  # Rough estimate
        "needs_planner": complexity_score >= 4,
        "asm_blocks": content.count('asm!'),
        "unsafe_blocks": content.count('unsafe')
    }
