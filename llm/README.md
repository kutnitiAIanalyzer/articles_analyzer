# llm

Wrappers for language model backends.

## Purpose

This module isolates all LLM-specific code so you can:

* Swap backends without touching analyzers or processors.
* Centralize default generation parameters.
* Keep `main.py` and analyzers clean.

## Structure

* `LLMClient.py` — Abstract base class (interface).
* `LlamaCppClient.py` — Minimal wrapper for `llama_cpp.Llama`.

## Usage example

```python
from llm.LlamaCppClient import LlamaCppClient

# Create client with model path and construction parameters
llm = LlamaCppClient(model_path="model.gguf", n_ctx=4096, n_threads=8)

# Use defaults
result1 = llm("Hello world")

# Override generation parameters for this call
result2 = llm("Hello world", max_tokens=256, temperature=0.0)
```

## Default generation parameters

| Parameter       | Value     |
| --------------- | --------- |
| temperature     | 0.2       |
| top\_p          | 0.95      |
| repeat\_penalty | 1.1       |
| max\_tokens     | 512       |
| stop            | \["</s>"] |

## Extending

To add another backend, create a new class in this folder that inherits from `LLMClient` and implements `__call__`.
