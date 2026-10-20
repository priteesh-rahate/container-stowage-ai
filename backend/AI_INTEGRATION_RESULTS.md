
# AI-Driven Container Vessel Stowage Planning
## AI Integration and Testing Report

### 1. Project Overview

This project develops an AI-assisted container vessel
stowage planning system using Python, FastAPI, React,
and the Qwen 2.5 7B language model through Ollama.

The system generates container placement plans using
a Python algorithm and optional AI recommendations.

### 2. Technologies Used

- Python - Container placement algorithm
- FastAPI - Backend API
- React and TypeScript - Frontend interface
- Ollama - Local AI runtime
- Qwen 2.5 7B - AI slot recommendations
- Pandas - Cargo manifest processing
- GitHub - Version control

### 3. AI Integration Improvements

The original implementation requested AI recommendations
for only the first five containers.

The updated implementation supports:
- Processing multiple batches of five containers
- Up to four AI batches per planning request
- A limited candidate-slot list for each batch
- Python validation of proposed placements
- Fallback placement when AI recommendations cannot be used

The current configuration requests AI recommendations
for up to 20 containers.

### 4. Testing Results

| Test | Result |
|------|--------|
| 40-foot missing-bay validation | PASS |
| Incompatible-bay validation | PASS |
| Multi-batch processing | PASS |
| Multi-batch overlap safety | PASS |
| AI versus non-AI comparison | PASS |
| 2,000-container baseline test | PASS |
| 2,000-container AI-enabled test | PASS |

### 5. Performance Comparison

| Metric | Without AI | With AI |
|--------|------------|---------|
| Containers | 2,000 | 2,000 |
| Assigned | 2,000 | 2,000 |
| Unassigned | 0 | 0 |
| Estimated rehandles | 18 | 18 |
| Execution time | 2.84 sec | 458.65 sec |

The AI-enabled version took longer because the Qwen
model was running locally in CPU mode.

These results do not demonstrate an optimization
improvement over the baseline algorithm.

### 6. Limitations

- The vessel layout is synthetic, not a real ship model.
- Real vessel stability is not verified.
- Stack loads and operational constraints are not
  comprehensively enforced.
- Rehandles are estimated rather than simulated.
- AI recommendations currently cover only 20 containers.
- AI acceptance rates are not yet measured.
- CPU-based AI processing is relatively slow.
- Port sequencing and realistic voyage optimization
  require further development.

### 7. Conclusion

The project successfully demonstrates integration
between a local AI model and a Python-based container
placement algorithm.

Tests confirm successful assignment of 2,000 sample
containers without overlapping footprints in the
synthetic layout.

Further development is required to demonstrate
optimization benefits and validate real-world
vessel safety and operational constraints.
