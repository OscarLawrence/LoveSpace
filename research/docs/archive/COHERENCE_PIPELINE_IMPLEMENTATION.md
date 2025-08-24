# Axiom Coherence Pipeline - Implementation Plan

## 🎯 Vision
First AI collaboration tool with **full coherence validation** - both user input and AI output are mathematically verified for logical consistency.

## 📋 Architecture Overview

### Complete Coherence Pipeline
```
User Input → Coherence Validation → Claude API → Contract Validation → Verified Output
     ↓               ↓                    ↓              ↓                ↓
 Real-time      Contradiction        Clean        Formal           User sees
 feedback       detection           prompt      contracts         only coherent
```

## 🏗️ Implementation Phases

### Phase 1: Backend Coherence Integration

#### 1.1 Copy Formal Contract System
**Location**: `axiom/backend/core/contracts.py`
**Source**: Copy from `projects/coherence/formal_contracts/contract_language.py`
**Modifications needed**:
- Update imports for Axiom structure
- Keep all contract decorators (`@coherence_contract`)
- Keep built-in predicates (is_sorted, same_elements, etc.)
- Keep complexity constraints and verification

#### 1.2 Add User Input Validator  
**Location**: `axiom/backend/core/input_validator.py`
**Source**: Extract from `projects/coherence/src/coherence/validator.py`
**Features**:
```python
class UserInputValidator:
    def validate_prompt(self, user_input: str) -> CoherenceResult:
        """Validate user input for logical contradictions"""
        
    def detect_contradictions(self, text: str) -> List[str]:
        """Find logical contradictions in user input"""
        
    def suggest_clarifications(self, contradictions: List[str]) -> List[str]:
        """Generate clarifying questions for incoherent input"""
```

#### 1.3 Add AI Output Validator
**Location**: `axiom/backend/core/output_validator.py`
**Features**:
```python
class AIOutputValidator:
    def validate_response(self, ai_response: str) -> ValidationResult:
        """Check if AI response has proper formal contracts"""
        
    def extract_contracts(self, code: str) -> List[FormalContract]:
        """Extract @coherence_contract decorators from code"""
        
    def verify_implementation(self, contract: FormalContract, code: str) -> bool:
        """Verify code satisfies formal contract"""
```

#### 1.4 Update Session Manager
**Location**: `axiom/backend/core/session_manager.py`
**Modifications**:
- Add coherence validation before sending to Claude
- Add contract validation after receiving Claude response
- Add coherence toggle per session
- Add validation results to message history

### Phase 2: Frontend Coherence Interface

#### 2.1 Real-time Input Validation
**Location**: `axiom/frontend/js/coherence.js`
**Features**:
- Debounced validation as user types
- Visual coherence indicators (red/yellow/green)
- Contradiction highlighting in text
- Clarification suggestions popup

#### 2.2 Coherence Settings Panel
**Location**: `axiom/frontend/js/settings.js`
**Features**:
```javascript
// Coherence mode toggle
enableCoherenceValidation: boolean

// Validation strictness levels
coherenceLevel: 'permissive' | 'standard' | 'strict'

// Auto-fix suggestions
autoSuggestFixes: boolean
```

#### 2.3 Contract Visualization
**Location**: `axiom/frontend/js/contracts.js`
**Features**:
- Display formal contracts in AI responses
- Show verification status (✅ verified, ❌ failed)
- Contract explanation tooltips
- Complexity badges (O(n), O(log n), etc.)

### Phase 3: System Integration

#### 3.1 Update System Prompts
**Location**: `axiom/backend/core/session_manager.py` (system prompts)
**Changes**:
- Always require `@coherence_contract` decorators
- Include contract examples in prompts
- Specify complexity requirements
- Require purity declarations

#### 3.2 Enhanced Tool Parser
**Location**: `axiom/backend/tools/parser.py`
**Updates**:
- Parse contract decorators from AI responses
- Extract formal specifications
- Validate before execution

#### 3.3 API Endpoints
**New endpoints**:
```
POST /api/validate-input          # Validate user input
POST /api/validate-output         # Validate AI output  
GET  /api/session/{id}/coherence  # Get coherence settings
PUT  /api/session/{id}/coherence  # Update coherence settings
```

## 🎨 User Experience Flow

### Scenario 1: Incoherent User Input
```
1. User types: "Create a O(1) sorting algorithm that's also secure"
2. Real-time indicator turns red
3. Popup shows: "Contradiction detected: Sorting requires O(n log n) minimum"
4. Suggests: "Did you mean: efficient sorting algorithm?"
5. User clicks suggestion, input updated
6. Indicator turns green, request sent to Claude
```

### Scenario 2: AI Response Validation
```
1. Claude returns code without @coherence_contract
2. Backend detects missing contracts
3. Automatically regenerates with prompt: "Add formal contracts to your code"
4. New response includes proper contracts
5. Contracts verified against implementation
6. Only verified code shown to user
```

### Scenario 3: Contract Violations
```
1. Claude claims O(1) complexity but uses nested loops
2. Contract verifier detects violation
3. Response marked as ❌ Contract Violation
4. User sees explanation: "Implementation is O(n²) but claims O(1)"
5. Offers to regenerate with correct complexity
```

## 📁 File Structure

```
axiom/backend/core/
├── contracts.py           # Formal contract system (copied from coherence)
├── input_validator.py     # User input coherence validation
├── output_validator.py    # AI output contract validation
└── session_manager.py     # Updated with coherence pipeline

axiom/frontend/js/
├── coherence.js          # Real-time input validation UI
├── contracts.js          # Contract visualization components
└── settings.js           # Coherence settings panel

axiom/frontend/css/
└── coherence.css         # Coherence indicator styling
```

## 🎯 Success Metrics

### Technical Validation
- All AI-generated code includes formal contracts
- Contract verification rate >95%
- Input contradiction detection accuracy
- Real-time validation performance <100ms

### User Experience
- Reduced conversation iterations (fewer clarifications needed)
- Higher user satisfaction with AI responses
- Educational value (users learn coherent prompting)

## 🚀 Implementation Priority

### Sprint 1 (Backend Foundation)
1. Copy formal contract system
2. Implement user input validator
3. Add coherence validation to session manager
4. Create basic validation API endpoints

### Sprint 2 (Frontend Integration)  
1. Real-time input validation UI
2. Coherence indicators and tooltips
3. Settings panel for coherence options
4. Contract visualization in responses

### Sprint 3 (Advanced Features)
1. Suggestion system for incoherent input
2. Contract explanation and education
3. Performance optimization
4. Integration testing and refinement

## 💡 Innovation Impact

**This makes Axiom the first AI tool that:**
- Prevents incoherent conversations before they start
- Guarantees mathematically verified AI responses  
- Educates users to think more coherently
- Solves Vincent's personal pain point at scale

**Revolutionary positioning**: "The only AI assistant that thinks coherently - because you do too."