# 🛠️ Engineering Tools Directory

This directory contains all 6 specialized engineering calculation tools for railway engineering applications.

## 📂 Tool Structure

Each engineering tool follows a consistent, modular architecture:

```
tool_name/
├── __init__.py          # Package initialization and exports
├── api.py              # FastAPI endpoints and route handlers
├── core.py             # Pure mathematical calculation functions
├── schemas.py          # Pydantic input/output validation models
├── service.py          # Business logic coordination and orchestration
├── validation.py       # Input validation and error handling
├── constants.py        # Engineering constants and conversion factors
├── units.py            # Unit conversion utilities
├── assets/             # Tool-specific static assets
└── reports/            # PDF report templates and generation
```

## 🛤️ Available Tools

### 1. Braking Calculator (`braking/`)
**Purpose**: Railway vehicle braking force and stopping distance calculations
**Standards**: DIN EN 15746-2:2021-05 compliance
**Inputs**: Vehicle weight, speed, gradient, wheel diameter, braking parameters
**Outputs**: Braking forces, deceleration rates, stopping distances

### 2. Hydraulic Calculator (`hydraulic/`)
**Purpose**: Hydraulic motor and pump sizing for locomotive drive systems
**Engineering Focus**: Hydraulic power transmission and efficiency
**Inputs**: Target speed, vehicle specs, gear ratios, system pressure
**Outputs**: Motor displacement, pump requirements, flow rates, efficiency

### 3. Qmax Calculator (`qmax/`)
**Purpose**: Maximum permissible axle loads for rail safety
**Safety Critical**: Prevents rail bending stress exceeding limits
**Inputs**: Wheel diameter, vehicle speed, rail properties
**Outputs**: Maximum axle loads, safety margins, compliance status

### 4. Load Distribution (`load_distribution/`)
**Purpose**: Axle and wheel load analysis for vehicle stability
**Engineering Focus**: Load distribution and vehicle dynamics
**Inputs**: Vehicle configuration, load parameters, operating conditions
**Outputs**: Axle loads, wheel loads, stability analysis, safety factors

### 5. Tractive Effort (`tractive_effort/`)
**Purpose**: Train tractive effort and electrical power requirements
**Systems Engineering**: Power transmission and electrification planning
**Inputs**: Train weight, speed, gradient, curve radius, electrical parameters
**Outputs**: Tractive effort, electrical power, energy consumption

### 6. Vehicle Performance (`vehicle_performance/`)
**Purpose**: Comprehensive locomotive performance analysis and optimization
**Systems Focus**: Performance curves, gear optimization, efficiency analysis
**Inputs**: Locomotive specifications, operating conditions, design parameters
**Outputs**: Performance curves, optimization recommendations, efficiency metrics

## 🔧 Development Guidelines

### Adding a New Tool

1. **Create Tool Directory Structure**:
   ```bash
   mkdir app/tools/new_tool
   # Create all required files following the template
   ```

2. **Implement Core Calculations** (`core.py`):
   ```python
   def calculate_new_tool(inputs: Dict[str, Any]) -> Dict[str, Any]:
       """Pure mathematical functions only - no I/O operations"""
       # Engineering calculations here
       return results
   ```

3. **Define Data Models** (`schemas.py`):
   ```python
   class NewToolRequest(BaseModel):
       parameter1: float
       parameter2: str

   class NewToolResponse(BaseModel):
       result1: float
       result2: Dict[str, Any]
   ```

4. **Create API Endpoints** (`api.py`):
   ```python
   @router.post("/new-tool")
   def new_tool_endpoint(request: NewToolRequest):
       return calculate_new_tool(request.dict())
   ```

5. **Add to Main API Router** (`app/api/tools.py`):
   ```python
   from app.tools.new_tool.api import router as new_tool_router
   # Include in main router
   ```

### Code Quality Standards

- **Pure Functions**: Core calculations should be pure and testable
- **Type Hints**: Full type annotation for all functions
- **Documentation**: Comprehensive docstrings with examples
- **Validation**: Input validation and error handling
- **Units**: Consistent unit systems (SI preferred)
- **Testing**: Unit tests for all calculation functions

### Engineering Standards

- **Accuracy**: Calculations verified against industry standards
- **Safety**: Critical safety calculations include appropriate margins
- **Documentation**: All formulas referenced to standards/equations
- **Units**: Clear specification of input/output units
- **Limitations**: Document calculation limitations and assumptions

## 📊 Testing Tools

Each tool includes comprehensive testing:

```bash
# Run specific tool tests
python -m pytest app/tools/braking/ -v

# Run all tool tests
python -m pytest app/tools/ -v

# Test with sample data
python -c "from app.tools.braking.core import calculate_braking; print(calculate_braking(test_inputs))"
```

## 📄 Report Generation

All tools generate professional PDF reports using LaTeX:

- **Templates**: Located in `app/services/templates/`
- **Rendering**: XeLaTeX/LuaLaTeX for high-quality output
- **Content**: Engineering-standard formatting and notation
- **Branding**: Company logos and professional appearance

## 🔗 Integration Points

- **API Layer**: `app/api/tools.py` - Main tool endpoints
- **Frontend**: Tool cards and forms in HTML templates
- **Database**: Calculation history in `calculations` table
- **PDF Service**: Report generation integration
- **License Service**: Tool access control

## 📚 Learning Resources

- **Engineering Standards**: DIN, EN, UIC railway standards
- **Physics References**: Engineering mechanics and dynamics
- **Best Practices**: Railway engineering design guidelines
- **Validation Data**: Test cases from industry standards

## 🚀 Contributing

When adding new tools or modifying existing ones:

1. Follow the established directory structure
2. Include comprehensive tests and documentation
3. Validate calculations against known standards
4. Update API documentation and schemas
5. Add tool to main application routing

---

**For detailed API documentation, see individual tool README files or visit `/docs` when running the application.**</content>
<parameter name="filePath">c:\Users\PEW-R&D-VINEET\OneDrive - Premnath Engineering Works\Desktop\Running Program\WEb - Render uploaded files with braking tool and pdf\app\tools\README.md