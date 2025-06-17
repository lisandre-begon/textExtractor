from datasets import load_dataset
from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)

# === CONFIGURATION ===
model_name = "t5-small"
train_data_path = "./data/train_data.json"
output_dir = "./models/t5_finetuned"
log_dir = "./logs"

# === LOAD MODEL + TOKENIZER ===
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# === PREPROCESSING FUNCTION ===
def preprocess(example):
    input_text = f"extract pathway json: {example['input']}"
    model_input = tokenizer(input_text, max_length=512, truncation=True)
    label = tokenizer(example['output'], max_length=512, truncation=True)
    model_input["labels"] = label["input_ids"]
    return model_input

# === LOAD & TOKENIZE DATASET ===
data = load_dataset("json", data_files=train_data_path, split="train")
tokenized_data = data.map(preprocess, batched=False)
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# === TRAINING ARGUMENTS ===
training_args = TrainingArguments(
    output_dir=output_dir,
    evaluation_strategy="no",
    learning_rate=3e-5,
    per_device_train_batch_size=4,
    num_train_epochs=10,
    weight_decay=0.01,
    save_strategy="epoch",
    logging_dir=log_dir,
    logging_steps=10,
    save_total_limit=1,
    report_to="none"
)

# === TRAINER ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_data,
    tokenizer=tokenizer,
    data_collator=data_collator
)

# === RUN TRAINING ===
trainer.train()
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)
