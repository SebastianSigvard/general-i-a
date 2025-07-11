# CLAUDE.md - Generala IA Development Guidelines

This document contains critical information about working with the Generala IA codebase. Follow these guidelines precisely.

## Core Development Rules

1. **Package Management**
   - ONLY use Poetry, NEVER pip directly
   - Installation: `poetry add package`
   - Running tools: `poetry run command`
   - Development deps: `poetry add --group dev package`
   - FORBIDDEN: Direct pip usage, manual venv management

2. **Code Quality**
   - Type hints required for all function signatures
   - Docstrings required for public classes and functions
   - Input validation required for all user-facing functions
   - Follow existing patterns exactly
   - All user inputs must use `validation.py` functions

3. **Testing Requirements**
   - Framework: `poetry run pytest`
   - ALL changes require corresponding unit tests
   - Edge cases and error conditions must be tested
   - Run from project root: `poetry run python -m pytest tests/test_generala.py`
   - Target: Maintain 100% test pass rate (currently 33/33)

4. **Import Structure**
   - Tests import from `src/` via path manipulation (line 6 in test file)
   - CLI runs from project root: `poetry run python src/cli.py`
   - NEVER run from `src/` directory (causes import issues)

## Game Rules & Scoring

Generala is a dice game with specific scoring rules that MUST be implemented correctly:

### Base Scores (Traditional Rules)
- **Escalera** (Straight): 20 base (+5 first roll bonus) = 25/20
- **Full House**: 30 base (+5 first roll bonus) = 35/30  
- **Poker** (4-of-kind): 40 base (+5 first roll bonus) = 45/40
- **Generala** (5-of-kind): 50 points (instant win on first roll)
- **Numbers (1-6)**: Count × face value
- **Double Generala**: 100 points

### Game Flow
- **3 rolls maximum** per turn (start_turn + 2 additional rolls)
- **Can score after any roll** (including first)
- **11 rounds total** (one per category)
- **Hold any combination** of dice between rolls

## Development Philosophy

- **Test-Driven**: Write/update tests before implementing features
- **Input Validation**: All user inputs must be validated and raise meaningful errors
- **Modularity**: Keep game logic, AI, CLI, and validation separate
- **Clarity**: Use descriptive variable names, especially for game state
- **Error Handling**: Use specific exception types with clear messages

## System Architecture

```
GeneralaGame (Core Engine)
├── GeneralaRules (Static scoring logic)
├── GeneralaScoreBoard (Score tracking)
├── validation.py (Input validation)
└── CLI/Agent interfaces
```

### State Flow
1. `start_turn()` → automatic first roll, `roll_number = 1`
2. `roll(held_dice)` → re-roll non-held dice, increment `roll_number`
3. `score(category)` → score in category, advance to next player
4. `next_player()` → cycle players, advance rounds, check game end

## Core Components

- `src/generala.py`: Game engine with rules, scoring, and state management (184 lines)
- `src/validation.py`: Centralized input validation functions (41 lines)
- `src/agent.py`: Deep Q-Learning agent with PyTorch (93 lines)
- `src/cli.py`: Interactive command-line interface (396 lines)
- `src/train_qagent.py`: AI training pipeline with hyperparameter tuning (259 lines)
- `tests/test_generala.py`: Comprehensive test suite - 33 tests covering core logic, edge cases, and advanced scenarios

## AI/ML Components

### Agent Architecture
- **Algorithm**: Double DQN with experience replay
- **State**: 24-dim vector (dice + held + roll_encoding + categories)
- **Actions**: 44 total (1 roll + 32 hold patterns + 11 scoring)
- **Training**: Configurable hyperparameters via command line

### Pre-trained Models
- **Available**: 10 trained models from systematic grid search
- **Performance**: Average scores 25-35 points
- **Usage**: Load with `agent.load_model('filename.pth')`

## Development Best Practices

- **Run Tests First**: `poetry run python -m pytest tests/test_generala.py -v`
- **Validate Inputs**: Use functions from `validation.py` for all user inputs
- **Meaningful Errors**: Provide clear error messages for invalid operations
- **Manual Testing**: Test CLI interactions after code changes
- **Preserve Patterns**: Follow existing code structure and naming conventions

## Common Pitfalls

### Import Issues
```bash
# ✅ CORRECT - Run from project root
poetry run python src/cli.py

# ❌ WRONG - Causes import errors
cd src && python cli.py
```

### Testing Patterns
```python
# ✅ CORRECT - Test validation behavior
with pytest.raises(ValueError, match="specific error message"):
    GeneralaRules.score_category(GeneralaCategory.ONES, [], 1)

# ❌ WRONG - Generic exception catching
with pytest.raises(Exception):
    some_function()
```

### Scoring Implementation
```python
# ✅ CORRECT - Base score + bonus pattern
return base_score + bonus if condition else 0

# ❌ WRONG - Hardcoded total scores
return 35 if condition else 0  # Should be 30 + 5
```

## Git Workflow

### Commit Messages
- Use descriptive commit messages explaining the "why" not just "what"
- For bug fixes: `git commit --trailer "Reported-by:<name>"`
- For features: Focus on user benefit and technical approach

### Branch Strategy
```bash
git checkout -b feature/descriptive-name
# Make changes, add tests
poetry run python -m pytest tests/test_generala.py  # Verify tests pass
git add . && git commit -m "Add feature: description"
git push -u origin feature/descriptive-name
```

## Critical File Locations

### Configuration
- `pyproject.toml`: Poetry dependencies and project metadata
- `tox.ini`: Testing environments (currently MyPy only)

### Data & Models
- `logs/`: Training logs from hyperparameter experiments
- `*.pth`: Trained model checkpoints
- `*.png`: Training progress visualizations

### Documentation
- `README.md`: Basic project overview
- `CLAUDE.md`: This development guide (definitive reference)

## Error Resolution

### Common Issues

1. **Import Errors**
   ```bash
   # Fix: Ensure running from project root
   cd /path/to/general-i-a
   poetry run python src/cli.py
   ```

2. **Test Failures**
   ```bash
   # Debug specific test
   poetry run python -m pytest tests/test_generala.py::test_name -v -s
   ```

3. **Validation Errors**
   ```python
   # Always validate user inputs
   from validation import validate_dice_list
   validate_dice_list(dice)  # Before processing
   ```

### MyPy Configuration
- Currently has path resolution issues
- Workaround: Run type checking from `src/` directory
- TODO: Fix project-wide MyPy configuration

## Performance Notes

- **Training Time**: ~2-4 hours for 50k episodes
- **Model Size**: ~100KB per trained model
- **Game Performance**: Real-time CLI interaction, no optimization needed
- **Memory Usage**: <500MB peak during training

## Extension Guidelines

### Adding New Features
1. **Plan**: Define requirements and test cases first
2. **Validate**: Add input validation for new parameters
3. **Test**: Write comprehensive unit tests
4. **Document**: Update docstrings and this guide
5. **Integrate**: Ensure CLI and agent compatibility

### Modifying Scoring
1. **Verify Rules**: Confirm traditional Generala rules
2. **Update Tests**: Modify expected values in test cases
3. **Retrain Models**: AI agents need retraining for rule changes
4. **Document Changes**: Update game rules section

---

**Last Updated**: 2025-01-11  
**Critical**: This document is the authoritative source for development practices. Always refer to this before making significant changes to the codebase.