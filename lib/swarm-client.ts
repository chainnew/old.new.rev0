/**
 * TypeScript client for Hive-Mind Swarm API
 * Connects Next.js frontend to Python FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_SWARM_API_URL || 'http://localhost:8000';

export interface SwarmScope {
  project: string;
  goal: string;
  tech_stack: Record<string, any>;
  features: string[];
  num_agents?: number;
}

export interface SwarmAgent {
  id: string;
  role: 'research' | 'design' | 'implementation' | 'test' | 'deploy' | 'quality';
  state: {
    status: string;
    data: Record<string, any>;
  };
}

export interface SwarmTask {
  id: string;
  agent_id: string;
  swarm_id: string;
  description: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  priority: number;
  data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface SwarmStatus {
  swarm_id: string;
  name: string;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  agents: SwarmAgent[];
  tasks: SwarmTask[];
  metadata: Record<string, any>;
}

export class SwarmClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Create a new swarm from initial scope
   */
  async createSwarm(scope: SwarmScope): Promise<{ swarm_id: string; status: SwarmStatus }> {
    const response = await fetch(`${this.baseUrl}/swarms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project: scope.project,
        goal: scope.goal,
        tech_stack: scope.tech_stack,
        features: scope.features,
        num_agents: scope.num_agents || 5
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create swarm');
    }

    return response.json();
  }

  /**
   * Get full swarm status including agents and tasks
   */
  async getSwarmStatus(swarmId: string): Promise<SwarmStatus> {
    const response = await fetch(`${this.baseUrl}/swarms/${swarmId}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch swarm status');
    }

    return response.json();
  }

  /**
   * Get all agents in a swarm
   */
  async getSwarmAgents(swarmId: string): Promise<{ swarm_id: string; agents: SwarmAgent[] }> {
    const response = await fetch(`${this.baseUrl}/swarms/${swarmId}/agents`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch swarm agents');
    }

    return response.json();
  }

  /**
   * Get tasks for a specific agent
   */
  async getAgentTasks(agentId: string): Promise<{ agent_id: string; tasks: SwarmTask[] }> {
    const response = await fetch(`${this.baseUrl}/agents/${agentId}/tasks`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch agent tasks');
    }

    return response.json();
  }

  /**
   * Update task status
   */
  async updateTask(taskId: string, status: string, data?: Record<string, any>): Promise<void> {
    const response = await fetch(`${this.baseUrl}/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, data })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update task');
    }
  }

  /**
   * Update agent state
   */
  async updateAgentState(agentId: string, state: Record<string, any>): Promise<void> {
    const response = await fetch(`${this.baseUrl}/agents/${agentId}/state`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update agent state');
    }
  }

  /**
   * Update swarm status
   */
  async updateSwarmStatus(swarmId: string, status: 'idle' | 'running' | 'paused' | 'completed' | 'error'): Promise<void> {
    const response = await fetch(`${this.baseUrl}/swarms/${swarmId}/status?status=${status}`, {
      method: 'PUT'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update swarm status');
    }
  }

  /**
   * Poll swarm status with interval
   */
  async pollSwarmStatus(
    swarmId: string, 
    callback: (status: SwarmStatus) => void, 
    intervalMs: number = 2000
  ): Promise<() => void> {
    const poll = async () => {
      try {
        const status = await this.getSwarmStatus(swarmId);
        callback(status);
      } catch (error) {
        console.error('Poll error:', error);
      }
    };

    // Initial fetch
    await poll();

    // Setup interval
    const interval = setInterval(poll, intervalMs);

    // Return cleanup function
    return () => clearInterval(interval);
  }
}

// Export singleton instance
export const swarmClient = new SwarmClient();

// Helper to convert SwarmTask to Agent Plan format
export function convertToAgentPlan(status: SwarmStatus) {
  const tasksByAgent = status.tasks.reduce((acc, task) => {
    const agent = status.agents.find(a => a.id === task.agent_id);
    if (!agent) return acc;

    if (!acc[agent.role]) {
      acc[agent.role] = {
        id: agent.id,
        title: `${agent.role.charAt(0).toUpperCase() + agent.role.slice(1)} Agent`,
        description: `Handles ${agent.role} tasks`,
        status: agent.state.status,
        priority: 'high',
        level: 0,
        dependencies: [],
        subtasks: []
      };
    }

    acc[agent.role].subtasks.push({
      id: task.id,
      title: task.description,
      description: JSON.stringify(task.data),
      status: task.status,
      priority: task.priority > 7 ? 'high' : task.priority > 4 ? 'medium' : 'low',
      tools: [`${agent.role}-tools`]
    });

    return acc;
  }, {} as Record<string, any>);

  return Object.values(tasksByAgent);
}
