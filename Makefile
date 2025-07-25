# =============================================================================
# TASK RUNNER
# =============================================================================

# Get remaining arguments after the target
ARGS := $(wordlist 2, $(words $(MAKECMDGOALS)), $(MAKECMDGOALS))

# Use Python task runner for all tasks
TASK_RUNNER := python -m tools.tasks

# =============================================================================
# ISSUE MANAGEMENT
# =============================================================================

list:
	@$(TASK_RUNNER) "python tools/issues.py list"

bug:
	@$(TASK_RUNNER) "python tools/issues.py create bug"

task:
	@$(TASK_RUNNER) "python tools/issues.py create task"

idea:
	@$(TASK_RUNNER) "python tools/issues.py create idea"

resolve:
	@$(TASK_RUNNER) "python tools/issues.py resolve $(ARGS)"

delete:
	@$(TASK_RUNNER) "python tools/issues.py delete $(ARGS)"

# =============================================================================
# DEMONSTRATIONS
# =============================================================================

# Run function mode demo
serve-function:
	@$(TASK_RUNNER) "python tryit/function.py" $(ARGS)

# Run script mode demo
serve-script:
	@$(TASK_RUNNER) "python tryit/script.py" $(ARGS)

# Run apps mode demo (FastAPI integration)
serve-apps:
	@$(TASK_RUNNER) "python tryit/apps.py" $(ARGS)

# Run container mode demo (Docker)
spin:
	@$(TASK_RUNNER) "docker stop terminaide-container 2>/dev/null || true" $(ARGS)
	@$(TASK_RUNNER) "docker rm terminaide-container 2>/dev/null || true" $(ARGS)
	@$(TASK_RUNNER) "docker build -t terminaide ." $(ARGS)
	@$(TASK_RUNNER) "docker run --name terminaide-container -p 8000:8000 terminaide" $(ARGS)

# =============================================================================
# TESTING
# =============================================================================

# Run all tests
test:
	@$(TASK_RUNNER) "pytest tests/ -v" $(ARGS)

# =============================================================================
# PUBLICATION
# =============================================================================

# Release new version
release:
	@$(TASK_RUNNER) "python tools/publisher.py" $(ARGS)

# =============================================================================
# 
# =============================================================================

# Dummy targets to prevent Make errors when passing arguments
%:
	@:
