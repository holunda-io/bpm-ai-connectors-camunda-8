# Local Models

When starting the `bpm-ai-inference` extension container in addition to the main connector container, you gain the possibility to use free, 100% local AI models instead of API based services.

These models are tiny compared to your average LLM but specialized for a specific task (like classification for example).

This means that accuracy will not always match that of a big LLM, but sometimes comes surprisingly close.

Here are some general notes and limitations:
* Average model size is 1-2 GB
* Models are loaded on demand
* For best experience, 16+ GB of RAM and at least 4 CPU cores should be available (check docker engine config)
* Most models work best with English. We try to provide multilingual alternatives, but mileage may vary
* The models are usually less flexible and behave a bit differently than LLMs, the connectors try to mask that as good as possible. See details for specific connectors below

Start the inference container manually:
```bash 
docker compose --profile inference up -d
```

... or select the appropriate option in the wizard setup script.

## Decide Connector

Select `Classifier` as `LLM / Model`.

Select a fitting model based on the desired speed/accuracy tradeoff and language.

You can also use any model from the HuggingFace Hub that supports the `zero-shot-classification` task.

#### Usage Differences to LLMs
* List of possible values is always required
* The decision task is best provided as a single, fully formed question
* The model does not provide a reasoning for its decision, the corresponding result field is null

## Extract Connector

Select `Text Extraction Model` as `LLM / Model`.

Select a fitting model based on the desired speed/accuracy tradeoff and language.

You can also use any model from the HuggingFace Hub that supports the `question-answering` task.

#### Usage Differences to LLMs
* Extraction field descriptions are best provided as fully formed questions
* Extraction Mode `Multiple Entities` is experimental and may not yield good results in all cases
* Fields are extracted one-by-one so different to an LLM the model lacks the context of already extracted fields, which may lead to wrong or duplicate extraction. To mitigate that, you can include template variables (e.g. `{alreadyExtractedFieldName}`) in your descriptions referencing already extracted fields (use dot notation for nested objects). All in all, the extracting schema needs more tuning and engineering for more complex cases than would be necessary with an LLM.

## Translate Connector

Select `Neural Machine Translation` as `LLM / Model`.

Select a fitting model based on the desired speed/accuracy tradeoff and language (currently only Opus-MT is available as local model).

#### Usage Differences to LLMs
* Each language pair and direction uses a dedicated model, so if you expect a lot of combinations, this may be inefficient
* We currently support the following languages: DANISH, DUTCH, ENGLISH, FINNISH, FRENCH, GERMAN, ITALIAN, NORWEGIAN, POLISH, PORTUGUESE, SPANISH, SWEDISH, UKRAINIAN