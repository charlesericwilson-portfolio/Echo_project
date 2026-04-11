import torch
import os
import json
import pandas as pd
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template, standardize_sharegpt
from datasets import Dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# ====================== CONFIG ======================
model_path = ""
jsonl_file = ""

max_seq_length = 3126
r = 128
lora_alpha = 256
use_rslora = True
# ===================================================

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

print("Loading model on dual 5070 Ti...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_path,
    dtype=None,
    load_in_4bit=True,
    device_map="balanced",
)

model = FastLanguageModel.get_peft_model(
    model,
    r=r,
    lora_alpha=lora_alpha,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
    use_rslora=use_rslora,
)

# ====================== ROBUST LOADING WITH PANDAS ======================
print("\nLoading JSONL with pandas (bypasses PyArrow strict schema issues)...")

try:
    df = pd.read_json(jsonl_file, lines=True, encoding="utf-8", encoding_errors="ignore")
    print(f"pandas successfully loaded {len(df)} rows.")
except Exception as e:
    print(f"pandas read_json failed: {e}")
    # Fallback: manual line-by-line
    data_list = []
    skipped = 0
    with open(jsonl_file, "r", encoding="utf-8", errors="ignore") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                example = json.loads(line)
                data_list.append(example)
            except Exception:
                skipped += 1
                if skipped <= 20:
                    print(f"Skipped line {line_num}")
    df = pd.DataFrame(data_list)
    print(f"Manual fallback loaded {len(df)} rows, skipped {skipped}.")

if len(df) == 0:
    raise ValueError("No data could be loaded from the JSONL file!")

dataset = Dataset.from_pandas(df)
print(f"Converted to Hugging Face Dataset with {len(dataset)} examples.")

# Structural validation (keeps most examples)
def is_valid(example):
    messages = example.get("messages")
    return (
        messages is not None and
        isinstance(messages, list) and
        len(messages) > 0 and
        all(isinstance(msg, dict) and "role" in msg and "content" in msg for msg in messages)
    )

dataset = dataset.filter(is_valid, num_proc=4)
print(f"After structural filter: {len(dataset)} examples remain.")

if len(dataset) == 0:
    raise ValueError("No valid examples after filtering!")

# Standardize and format
dataset = standardize_sharegpt(dataset)

tokenizer = get_chat_template(
    tokenizer,
    chat_template="qwen-2.5",
    mapping={"role": "from", "content": "value", "user": "human", "assistant": "gpt"},
)

def formatting_prompts_func(examples):
    texts = []
    for convos in examples["messages"]:
        try:
            text = tokenizer.apply_chat_template(
                convos,
                tokenize=False,
                add_generation_prompt=False,
            )
            texts.append(text)
        except Exception:
            texts.append("")  # will be filtered next
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True, num_proc=4)

# Remove any remaining empty texts
dataset = dataset.filter(lambda x: isinstance(x.get("text"), str) and len(x["text"].strip()) > 20, num_proc=4)

print(f"Final training dataset size: {len(dataset)} examples")
if len(dataset) == 0:
    raise ValueError("Dataset empty after cleaning — check your data.")

# ====================== TRAINER ======================
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=max_seq_length,
    dataset_num_proc=4,
    packing=False,

    args=TrainingArguments(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=48,
        warmup_steps=100,
        num_train_epochs=1,
        learning_rate=1.5e-6,
        warmup_ratio = .30,
        max_grad_norm = .4,
        bf16=True,
        logging_steps=5,
        optim="adamw_8bit",
        weight_decay=0.12,
        lr_scheduler_type="cosine",
        output_dir="",
        report_to="none",
        save_strategy="steps",
        save_steps=150,
        save_total_limit=5,
    ),
)

print("\nStarting training...")
trainer.train()

model.save_pretrained("")
tokenizer.save_pretrained("")
print("Training completed!")
