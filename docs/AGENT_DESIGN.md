# Agent Design and Reasoning Framework

## Agent Architecture

### Base Agent Class
All agents inherit from `BaseAgent` which provides:
- LLM communication via Ollama
- Logging and observability
- Common utility methods

### Agent Responsibilities

#### 1. Data Extraction Agent
**Purpose**: Extract structured data from unstructured documents

**Input**: Document files (PDF, images, Excel)
**Output**: Structured extracted data dictionary

**Process**:
1. Identify document type
2. Use appropriate extraction method (OCR, PDF parsing, Excel reading)
3. Extract key fields using regex patterns
4. Enhance extraction with LLM if needed
5. Return structured data

**LLM Usage**: Enhances extraction accuracy for complex forms

#### 2. Validation Agent
**Purpose**: Validate and cross-check extracted data

**Input**: Extracted data from all documents
**Output**: Validation results with quality scores

**Process**:
1. Check address consistency across documents
2. Validate income consistency
3. Verify identity information (name, ID number)
4. Check family member consistency
5. Assess document completeness
6. Calculate overall quality score
7. Use LLM for advanced validation insights

**LLM Usage**: Provides validation insights and identifies subtle inconsistencies

#### 3. Eligibility Agent
**Purpose**: Assess applicant eligibility

**Input**: Extracted and validated data
**Output**: Eligibility assessment with scores

**Process**:
1. Extract features for ML model
2. Get ML model prediction (eligibility score)
3. Use LLM for comprehensive assessment
4. Combine ML and LLM results
5. Generate recommendation (approve/decline)

**ML Model**: RandomForest Classifier (predicts support tiers: HIGH/MEDIUM/LOW/NOT_ELIGIBLE)
**LLM Usage**: Provides context-aware assessment considering all factors

#### 4. Decision Agent
**Purpose**: Generate final decision and recommendations

**Input**: Eligibility assessment, validation results
**Output**: Final recommendation with reasoning

**Process**:
1. Analyze eligibility assessment
2. Consider validation quality
3. Use LLM to generate final decision
4. Calculate support amount (if approved)
5. Generate economic enablement recommendations
6. Provide next steps

**LLM Usage**: Synthesizes all information for final decision with detailed reasoning

#### 5. Chat Agent
**Purpose**: Interactive assistance for applicants

**Input**: User messages, optional application context
**Output**: Helpful responses

**Process**:
1. Understand user query
2. Retrieve application context if available
3. Generate contextual response
4. Provide guidance on process, documents, eligibility

**LLM Usage**: Natural language understanding and generation

## Reasoning Framework: ReAct

### ReAct Pattern Implementation

ReAct (Reasoning + Acting) is implemented in the orchestrator's conditional edges:

1. **After Extraction**: 
   - **Reason**: Check if extraction succeeded and data is available
   - **Act**: Continue to validation or handle error

2. **After Validation**:
   - **Reason**: Check data quality score
   - **Act**: Continue if quality acceptable, error if too low

3. **After Eligibility**:
   - **Reason**: Check if assessment completed
   - **Act**: Continue to decision making

### Benefits of ReAct
- **Transparency**: Clear reasoning at each step
- **Error Recovery**: Can handle failures gracefully
- **Iterative Refinement**: Can loop back if needed
- **Explainability**: Each decision point is documented

## Agent Orchestration with LangGraph

### Workflow Graph
```
[Extract] → [Validate] → [Assess Eligibility] → [Make Decision] → [END]
    ↓            ↓                ↓                    ↓
[Error Handler] ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

### State Management
- TypedDict for type safety
- State passed between nodes
- Error state handled separately

### Observability
- Langfuse decorators on each node
- Trace metadata includes application_id
- Full workflow visibility

## Model Selection Justification

### Scikit-learn Models

**RandomForest Classifier**:
- Handles non-linear relationships
- Feature importance for explainability
- Robust to outliers
- Predicts support tiers (HIGH/MEDIUM/LOW/NOT_ELIGIBLE) based on policy-aligned features
- Confidence scores derived from prediction probabilities
- Eligibility scores calculated from tier mapping and confidence

### LLM Integration

**Why LLM for Assessment?**
- Handles unstructured reasoning
- Considers context and edge cases
- Provides natural language explanations
- Can incorporate policy guidelines

**Why Local (Ollama)?**
- Privacy for sensitive data
- No API costs
- Full control
- Can use specialized models

## Future Enhancements

1. **Reflexion Pattern**: Add self-reflection for error correction
2. **PaS (Planning and Search)**: For complex multi-step reasoning
3. **Multi-Agent Collaboration**: Agents can query each other
4. **Fine-tuned Models**: Domain-specific fine-tuning
5. **Structured Output**: Use JSON mode for better parsing

