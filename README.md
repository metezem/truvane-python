# truvane

Official Python SDK for the [Truvane Image](https://truvane.ai) forensics API — tells you whether a product damage photo is real or AI-generated.

## Install

Not yet published to PyPI — install from source until it is:

```
git clone https://github.com/metezem/truvane-python.git
cd truvane-python
pip install .
```

Once published, this will become `pip install truvane`.

## Usage

```python
from truvane import TruvaneClient

client = TruvaneClient(api_key="tv_...")
result = client.verify(image=open("damage.jpg", "rb"))

print(result.authentic, result.confidence)
```

You can also pass a file path, raw bytes, or a remote image URL instead of a file object:

```python
client.verify(image="damage.jpg")
client.verify(image=raw_bytes)
client.verify(image_url="https://cdn.example.com/damage.jpg")
```

### Async

```python
import asyncio
from truvane import AsyncTruvaneClient

async def main():
    client = AsyncTruvaneClient(api_key="tv_...")
    result = await client.verify(image="damage.jpg")
    print(result)

asyncio.run(main())
```

### Errors

```python
from truvane import TruvaneAuthError, TruvaneRateLimitError, TruvaneValidationError

try:
    client.verify(image="damage.jpg")
except TruvaneAuthError:
    ...  # invalid or revoked API key
except TruvaneRateLimitError:
    ...  # too many requests / quota exceeded
except TruvaneValidationError:
    ...  # bad image, unsupported format, or bad image_url
```

## API key

Get a key from your Truvane contact, then either set it in your environment:

```
export TRUVANE_API_KEY=tv_...
```

or pass it explicitly: `TruvaneClient(api_key="tv_...")`.
