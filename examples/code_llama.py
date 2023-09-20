# Use a pipeline as a high-level helper
from transformers import pipeline, AutoTokenizer

model = "codellama/CodeLlama-7b-Instruct-hf"
tokenizer = AutoTokenizer.from_pretrained(model)
pipe = pipeline(
    "text-generation",
    model="codellama/CodeLlama-7b-Instruct-hf",
    device="cpu",
)

result = pipe(
    "def add(a, b):",
    max_new_tokens=100,
    do_sample=True,
    top_k=10,
    temperature=0.1,
    top_p=0.95,
    num_return_sequences=1,
    eos_token_id=tokenizer.eos_token_id,
    max_length=200,
)

print(result)
