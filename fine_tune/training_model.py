from datasets import load_dataset
import json
import os
import numpy as np
from datetime import datetime
from difflib import SequenceMatcher
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
test_data_path = "./data/test_data.json"
output_dir = "./models/t5_finetuned"
log_dir = "./logs"
predictions_dir = "./results"

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
train_data = load_dataset("json", data_files=train_data_path, split="train")
test_data = load_dataset("json", data_files=test_data_path, split="train")
data = load_dataset("json", data_files=train_data_path, split="train")
tokenized_train = train_data.map(preprocess, batched=False)
tokenized_test = test_data.map(preprocess, batched=False)
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# === METRICS ===
def compute_metrics(eval_pred):
    predictions, labels = eval_pred

    if isinstance(predictions, tuple):
        predictions = predictions[0]
    if predictions.ndim == 3:
        predictions = np.argmax(predictions, axis=-1)

    # Corriger les -100 dans les labels avant décodage
    labels = np.where(labels == -100, tokenizer.pad_token_id, labels)

    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    
    exact_matches = 0
    similarity_scores = []

    for pred, label in zip(decoded_preds, decoded_labels):
        if pred.strip() == label.strip():
            exact_matches += 1
        ratio = SequenceMatcher(None, pred.strip(), label.strip()).ratio()
        similarity_scores.append(ratio)

    exact_match = exact_matches / len(decoded_preds)
    avg_similarity = sum(similarity_scores) / len(similarity_scores)
    return {
        "exact_match": exact_match,
        "string_similarity": avg_similarity
    }



# === TRAINING ARGUMENTS ===
training_args = TrainingArguments(
    output_dir=output_dir,
    evaluation_strategy="epoch",
    learning_rate=3e-5,
    per_device_train_batch_size=4,
    num_train_epochs=10,
    weight_decay=0.01,
    save_strategy="epoch",
    logging_dir=log_dir,
    logging_steps=10,
    save_total_limit=1,
    report_to="none",
    lr_scheduler_type="linear",
    warmup_steps=0
)

# === TRAINER ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

# === RUN TRAINING ===
trainer.train()
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)

# === SAVE PREDICTIONS ===
predictions = trainer.predict(tokenized_test)

#Real id
if isinstance(predictions.predictions, tuple):
    logits = predictions.predictions[0]
else:
    logits = predictions.predictions

if logits.ndim == 3:
    pred_ids = np.argmax(logits, axis=-1)
else:
    pred_ids = logits

decoded_preds = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
labels = np.where(predictions.label_ids == -100, tokenizer.pad_token_id, predictions.label_ids)
decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)



output_file = os.path.join(predictions_dir, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
with open(output_file, "w") as f:
    json.dump([
        {"input": i["input"], "prediction": p, "label": l}
        for i, p, l in zip(test_data, decoded_preds, decoded_labels)
    ], f, indent=2)