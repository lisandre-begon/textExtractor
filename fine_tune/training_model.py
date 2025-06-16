from datasets import load_dataset
from transformers import T5Tokenizer, T5ForConditionalGeneration, TrainingArguments, Trainer, DataCollatorForSeq2Seq

# Load tokenizer & model
model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

def preprocess(example):
    #T5 work with instruction like this one
    input_text = f"extract pathway json: {example['input']}"
    #The model can go upper than 512 token so for now we are stuck, but later we might use other model
    model_input = tokenizer(input_text, max_length=512, truncation=True)
    #Tokenize the output (target)
    with tokenizer.as_target_tokenizer():
        label = tokenizer(example['output'], max_length=512, truncation=True)
    # Add the tokenized labels to the inputs
    model_input["labels"] = label["input_ids"]
    return model_input

data = load_dataset("json", data_files="train_data.json", split="train")
tokenized_data = data.map(preprocess, batched=False)

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)


#Set up training
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="no",
    learning_rate=3e-5,
    per_device_train_batch_size=4,
    num_train_epochs=10,
    weight_decay=0.01,
    save_strategy="epoch",
    logging_dir="./logs",
)

# Trainer setup
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_data,
    tokenizer=tokenizer,
    data_collator=data_collator
)

#Train and save
trainer.train()
trainer.save_model("./fine_tuned_t5_pathway")
tokenizer.save_pretrained("./fine_tuned_t5_pathway")