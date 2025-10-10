# Quick Start Guide: Phase 1 + 2A Synergy Systems

**Current Score**: 37/50 (from 17/50 baseline)
**Setup Time**: ~15 minutes
**Last Updated**: 2025-10-20

---

## TL;DR - Run This

```bash
# 1. Setup everything (one command)
bash backend/scripts/setup_phase1_and_2a.sh

# 2. Start all services
bash backend/scripts/start_all_services.sh

# 3. In another terminal, run demo
bash backend/scripts/demo_stack_inference.sh
```

**Done!** Your system now has:
- ✅ OpenTelemetry tracing
- ✅ Self-healing orchestration monitor
- ✅ Stack inference with pgvector
- ✅ Auto-fill technology stacks

---

## What Each Script Does

### 1. `setup_phase1_and_2a.sh`
**One-time setup**: Installs deps, sets up pgvector, seeds embeddings

### 2. `start_all_services.sh`
**Start services**: Monitor (background) + Swarm API (foreground with traces)

### 3. `demo_stack_inference.sh`
**Demo**: Sends 3 test requests showing stack auto-fill in action

### 4. `stop_all_services.sh`
**Cleanup**: Stops all services and cleans up ports

See [backend/PHASE_1_SETUP.md](backend/PHASE_1_SETUP.md) for full documentation.

---

**Next**: Review [docs/SYNERGY_ROADMAP.md](docs/SYNERGY_ROADMAP.md) for Week 2-4 plan
