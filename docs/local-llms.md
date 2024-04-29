# Local LLMs
> [!NOTE]
> This section is about local LLMs as a replacement for API-based LLMs.
> [⏩ See here for smaller, local non-LLM models that run on almost any machine](local-models.md)

When starting the `bpm-ai-inference` extension container in addition to the main connector container, you gain the possibility to use free, 100% local LLMs instead of API based services.

These LLMs are a lot smaller compared to API-based LLMs.
This means that accuracy will not always match that of a big, proprietary LLM, but sometimes comes surprisingly close. 

Some models already surpassed GPT-3.5-Turbo (the model powering free ChatGPT) and approach GPT-4. 
Others are smaller and feasible to run on a computer with just a CPU and enough RAM (typically 16 - 64GB, depending on the model).
The smaller models of recent month are often good enough for easier tasks, like pretty reliable information extraction, translation (depending on the base model's multilingual training) and basic decisions.
Bigger models often have stronger reasoning capabilities and are more reliable.

Here are some general notes and limitations:
* Full-precision models are usually too large for available RAM and too slow for CPU inference, as it is heavily memory-bound.
  * Therefore, we make use of intelligently "compressed" versions of varying sizes (usually ~2-50 GB, depending on the model)
* Models are loaded on demand
* For best experience, 16+ GB of RAM and at least 4 CPU cores should be available (**check docker engine config!**)
* Most models work best with English but have varying multilingual proficiency.
* Right now, only text is supported, with image capabilities added soon.

Start the inference container manually:
```bash 
docker compose --profile inference up -d
```

... or select the appropriate option in the wizard setup script.

### Available LLMs

| Name       | Parameters | RAM Usage (low precision) | RAM Usage (balanced precision) | RAM Usage (high precision) | Multilingual Capabilities                |
|------------|------------|---------------------------|--------------------------------|---------------------------|------------------------------------------|
| Phi-3 Mini | 3.8B       | 1.5 GB                    | 2.7 GB                         | 4 GB                      | Mostly English                           |
| Llama 3    | 8B         | 3.2 GB                    | 5.7 GB                         | 8.5 GB                    | Mostly English                           |
| Mistral    | 7B         | 3 GB                      | 5.1 GB                         | 7.7 GB                    | English & most common European languages |

More and larger models will be added soon, as well as specifically tuned variants for the BPM AI tasks.

## How to Use

In any connector, select `Local LLM` as `LLM / Model`.

Select a model according to the table above.

Select the precision according to the table above and your available RAM and speed/accuracy tradeoff.

### Differences to proprietary API-based LLMs
* Right now, no vision/image capabilities (coming soon)
* Varying multilingual capabilities between models (Llama 3 will get multilingual variants later)
* Usually less deep/advanced reasoning