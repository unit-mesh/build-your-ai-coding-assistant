import os
from threading import Thread
from typing import Iterator, List, Tuple
from urllib.request import Request

import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from fastapi.exceptions import RequestValidationError

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import requests
from pydantic import BaseModel
from starlette import status
from starlette.responses import JSONResponse
import async_timeout
import asyncio
import time

MAX_MAX_NEW_TOKENS = 4096
DEFAULT_MAX_NEW_TOKENS = 1024
total_count = 0
MAX_INPUT_TOKEN_LENGTH = int(os.getenv("MAX_INPUT_TOKEN_LENGTH", "4096"))

if torch.cuda.is_available():
    model_id = "/openbayes/input/input0/"
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map="auto")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.use_default_system_prompt = False


class Message(BaseModel):
    role: str
    content: str


class MessageInResponseChat(BaseModel):
    message: Message


class ChatResponse(BaseModel):
    choices: List[MessageInResponseChat]
    model: str


class SimpleOpenAIBody(BaseModel):
    messages: List[Message]
    temperature: float
    stream: bool


GENERATION_TIMEOUT_SEC = 480


async def stream_generate(
        chat_history: List[Message],
        max_new_tokens: int = 512,
        temperature: float = 0.1,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1,
):
    async with async_timeout.timeout(GENERATION_TIMEOUT_SEC):
        try:
            global total_count
            total_count += 1
            if total_count % 50 == 0:
                os.system("nvidia-smi")

            conversation = chat_history

            input_ids = tokenizer.apply_chat_template(conversation, return_tensors="pt")
            if input_ids.shape[1] > MAX_INPUT_TOKEN_LENGTH:
                input_ids = input_ids[:, -MAX_INPUT_TOKEN_LENGTH:]
            input_ids = input_ids.to(model.device)

            streamer = TextIteratorStreamer(tokenizer, timeout=20.0, skip_prompt=True, skip_special_tokens=True)
            generate_kwargs = dict(
                {"input_ids": input_ids},
                streamer=streamer,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                top_p=top_p,
                top_k=top_k,
                num_beams=1,
                temperature=temperature,
                repetition_penalty=repetition_penalty,
                eos_token_id=32021
            )
            t = Thread(target=model.generate, kwargs=generate_kwargs)
            t.start()

            result = ""
            outputs = []
            for text in streamer:
                outputs.append(text)
                result = "".join(outputs)
                # result = "".join(outputs).replace("<|EOT|>", "")

            yield 'data:' + ChatResponse(
                choices=[MessageInResponseChat(message=Message(role='assistant', content=result))],
                model="autodev-deepseek").model_dump_json()

            yield '\n\n'
            time.sleep(0.2)
            yield 'data:[DONE]'
            print(result)

        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Stream timed out")


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    print(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post("/api/chat", response_class=Response)
async def root(body: SimpleOpenAIBody) -> StreamingResponse:
    return StreamingResponse(stream_generate(body.messages, temperature=body.temperature),
                             media_type="text/event-stream")


if __name__ == "__main__":
    try:
        meta = requests.get('http://localhost:21999/gear-status', timeout=5).json()
        url = meta['links'].get('auxiliary')
        if url:
            print("打开该链接访问:", url)
    except Exception:
        pass

    uvicorn.run(app, host="0.0.0.0", port=8080)
