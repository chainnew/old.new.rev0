"""
Swarm Coordinator - Semi-Swarm Architecture with Agent Handshakes
Implements coordination, message passing, and health checks between agents
"""
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


@dataclass
class AgentMessage:
    """Message passed between agents"""
    from_agent: str
    to_agent: str
    message_type: str  # 'task', 'result', 'query', 'handshake'
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    conversation_id: str = ""


@dataclass
class AgentHealth:
    """Agent health status"""
    agent_id: str
    status: AgentStatus
    last_heartbeat: datetime
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_execution_time_ms: float = 0.0


class SwarmCoordinator:
    """
    Coordinates multiple agents with:
    - Message passing via async queues
    - Health monitoring
    - Task routing
    - Result aggregation
    """
    
    def __init__(self):
        # Message queues for each agent
        self.queues: Dict[str, asyncio.Queue] = {}
        
        # Agent health tracking
        self.agent_health: Dict[str, AgentHealth] = {}
        
        # Active tasks
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        
        # Results cache
        self.results_cache: Dict[str, Any] = {}
        
        print("🔥 SwarmCoordinator initialized")
    
    def register_agent(self, agent_id: str) -> asyncio.Queue:
        """
        Register an agent and get its message queue
        
        Args:
            agent_id: Unique agent identifier
            
        Returns:
            Agent's message queue
        """
        if agent_id not in self.queues:
            self.queues[agent_id] = asyncio.Queue()
            self.agent_health[agent_id] = AgentHealth(
                agent_id=agent_id,
                status=AgentStatus.IDLE,
                last_heartbeat=datetime.now()
            )
            print(f"✅ Agent '{agent_id}' registered")
        
        return self.queues[agent_id]
    
    async def send_message(self, message: AgentMessage):
        """Send message to target agent's queue"""
        if message.to_agent not in self.queues:
            print(f"⚠️ Agent '{message.to_agent}' not registered")
            return
        
        await self.queues[message.to_agent].put(message)
        print(f"📨 Message: {message.from_agent} → {message.to_agent} ({message.message_type})")
    
    async def broadcast_message(self, from_agent: str, message_type: str, payload: Dict[str, Any]):
        """Broadcast message to all registered agents"""
        tasks = []
        for agent_id in self.queues.keys():
            if agent_id != from_agent:
                msg = AgentMessage(
                    from_agent=from_agent,
                    to_agent=agent_id,
                    message_type=message_type,
                    payload=payload
                )
                tasks.append(self.send_message(msg))
        
        await asyncio.gather(*tasks)
    
    def update_agent_status(self, agent_id: str, status: AgentStatus):
        """Update agent status"""
        if agent_id in self.agent_health:
            self.agent_health[agent_id].status = status
            self.agent_health[agent_id].last_heartbeat = datetime.now()
    
    def heartbeat(self, agent_id: str):
        """Agent heartbeat to indicate it's alive"""
        if agent_id in self.agent_health:
            self.agent_health[agent_id].last_heartbeat = datetime.now()
    
    async def handshake(self, agent_id: str, capabilities: Dict[str, Any]) -> bool:
        """
        Agent handshake - announce capabilities to swarm
        
        Args:
            agent_id: Agent identifier
            capabilities: Agent capabilities (skills, models, etc.)
            
        Returns:
            True if handshake successful
        """
        if agent_id not in self.queues:
            self.register_agent(agent_id)
        
        # Broadcast capabilities to other agents
        await self.broadcast_message(
            from_agent=agent_id,
            message_type="handshake",
            payload={
                "agent_id": agent_id,
                "capabilities": capabilities,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        print(f"🤝 Handshake complete: {agent_id}")
        return True
    
    async def route_task(self, task: Dict[str, Any]) -> str:
        """
        Route task to best available agent
        
        Args:
            task: Task specification
            
        Returns:
            Selected agent ID
        """
        task_type = task.get('type', 'code')
        
        # Simple routing logic - can be enhanced with load balancing
        agent_mapping = {
            'code': 'code_agent',
            'port': 'eterna_port_agent',
            'debug': 'debug_agent',
            'research': 'research_agent'
        }
        
        selected_agent = agent_mapping.get(task_type, 'code_agent')
        
        # Check if agent is available
        if selected_agent in self.agent_health:
            if self.agent_health[selected_agent].status == AgentStatus.IDLE:
                self.update_agent_status(selected_agent, AgentStatus.WORKING)
                return selected_agent
        
        # Fallback to any idle agent
        for agent_id, health in self.agent_health.items():
            if health.status == AgentStatus.IDLE:
                self.update_agent_status(agent_id, AgentStatus.WORKING)
                return agent_id
        
        # All busy - return first agent
        return selected_agent
    
    async def execute_swarm_task(
        self, 
        task: Dict[str, Any], 
        agents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute task with swarm coordination
        
        Args:
            task: Task to execute
            agents: Dictionary of available agent instances
            
        Returns:
            Execution result
        """
        task_id = task.get('id', 'unknown')
        conversation_id = task.get('conversation_id', '')
        
        # Route to appropriate agent
        selected_agent_id = await self.route_task(task)
        
        if selected_agent_id not in agents:
            return {
                'task_id': task_id,
                'status': 'failed',
                'output': {'error': f'Agent {selected_agent_id} not found'}
            }
        
        # Execute task
        try:
            agent = agents[selected_agent_id]
            result = await agent.execute(task)
            
            # Update stats
            if selected_agent_id in self.agent_health:
                health = self.agent_health[selected_agent_id]
                if result.get('status') == 'completed':
                    health.tasks_completed += 1
                else:
                    health.tasks_failed += 1
            
            self.update_agent_status(selected_agent_id, AgentStatus.COMPLETED)
            
            # Cache result
            self.results_cache[task_id] = result
            
            return result
            
        except Exception as e:
            self.update_agent_status(selected_agent_id, AgentStatus.FAILED)
            return {
                'task_id': task_id,
                'status': 'failed',
                'output': {'error': str(e)}
            }
    
    def get_swarm_stats(self) -> Dict[str, Any]:
        """Get swarm health and statistics"""
        stats = {
            'total_agents': len(self.agent_health),
            'agents': {}
        }
        
        for agent_id, health in self.agent_health.items():
            stats['agents'][agent_id] = {
                'status': health.status.value,
                'tasks_completed': health.tasks_completed,
                'tasks_failed': health.tasks_failed,
                'last_heartbeat': health.last_heartbeat.isoformat()
            }
        
        return stats
    
    async def ping_all_agents(self) -> Dict[str, bool]:
        """Ping all agents to check if they're alive"""
        results = {}
        
        for agent_id in self.queues.keys():
            # Send ping message
            await self.send_message(AgentMessage(
                from_agent="coordinator",
                to_agent=agent_id,
                message_type="ping",
                payload={"timestamp": datetime.now().isoformat()}
            ))
            
            # Check if agent responded recently (within 30 seconds)
            if agent_id in self.agent_health:
                time_since_heartbeat = (datetime.now() - self.agent_health[agent_id].last_heartbeat).seconds
                results[agent_id] = time_since_heartbeat < 30
            else:
                results[agent_id] = False
        
        return results


# Global coordinator instance
_coordinator = None


def get_coordinator() -> SwarmCoordinator:
    """Get or create global coordinator instance"""
    global _coordinator
    if _coordinator is None:
        _coordinator = SwarmCoordinator()
    return _coordinator
