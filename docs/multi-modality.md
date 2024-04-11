# Multimodality
## Working with Images, Documents and Audio

There are two main ways how you can process image, document or audio files almost as easily as text:
* native multimodal models
* conversion from images/documents/audio into text

In every case, you can input these files simply be specifying a path or URL as an input variable value:

```
{ 
    document: "/opt/bpm-ai/invoice.pdf",
    phoneCall: "http://localhost:8080/audio.wav"
}
```

The connectors will detect if the value of a variable contains a path or URL to a supported file type and retrieve the file.

### Local Files
The default docker-compose file mounts a `data` directory on the host machine into `/opt/bpm-ai` in the container, so you can just place files in the data directory next to the docker-compose file and reference the file in the connector using a `/opt/bpm-ai` prefix as shown above. 

### Public Web Files
Files can also be downloaded from the local network or the public internet by specifying a http URL.

### Cloud Storage
Additionally, the connectors accept URLs to files in Amazon S3 buckets or Azure Blob Storage:

```
{ 
    documentS3: "s3://test-bucket/pdfs/dummy.pdf",
    documentAzure: "https://myaccount.blob.core.windows.net/mycontainer/doc.jpg"
}
```
#### Amazon S3
Supported URL formats:
- `s3://<bucket-name>/<file-path>`
- `https://<bucket-name>.s3.<region>.amazonaws.com/<file-path>`

Make sure to add your AWS credentials to the environment.

#### Azure Blob Storage
Supported URL format:
- `https://<account-name>.blob.core.windows.net/<container-name>/<file-path>`

Make sure to add an `AZURE_STORAGE_ACCESS_KEY` environment variable.

## Images & Documents

The following file types are supported by all connectors when using either a native multimodal model are an OCR model in addition to a text-only model:

`bmp`, `gif`, `icns`, `ico`, `jfif`, `jpe`, `jpeg`, `jpg`, `png`, `pbm`, `pgm`, `pnm`, `ppm`, `tif`, `tiff`, `webp`, `pdf`

### Native Image Models
The following LLMs support images natively and do not require conversion:
- Anthropic Claude 3 Opus
- Anthropic Claude 3 Sonnet
- Anthropic Claude 3 Haiku
- OpenAI GPT-4 Turbo
- All `Visual Document Extraction Models` in the extract connector

### OCR
You can use any text-only model with images or documents by selecting an OCR model in the dropdown.

#### Amazon Textract
Best performing OCR service. Limited to a single image/page when using local files, otherwise needs input from an S3 bucket.

#### Azure Document Intelligence
Well performing OCR service.
To use, please add the following environment variables:
```
AZURE_DOCUMENT_INTELLIGENCE_KEY=<key>
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://westeurope.api.cognitive.microsoft.com/
```

#### tesseract
Local OCR model that requires the local inference extension container. Only suitable for simple, single column documents.

> [!TIP]
> **When to use what?**
> The native image capability of LLMs is great for general image understanding or when working with documents that can't be captured well by OCR, e.g. containing graphs and images. For document classification OCR is usually enough and extraction - especially with long documents - is usually more accurate when using a good OCR model in tandem with a long context LLM like Anthropic Claude or OpenAI GPT-4 Turbo. 

## Audio

The following audio file types are supported by all connectors:

`flac`, `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `ogg`, `wav`, `webm`

Currently, there are no model that support audio natively. Instead, you can configure a transcription model to turn the audio data into text that any model can process:

### OpenAI Whisper API
High quality transcription service.
Make sure to set the `OPENAI_API_KEY` environment variable.

### Local Whisper Model
Similar quality to the API (when using large variant) but fully local. Requires the local inference extension container.