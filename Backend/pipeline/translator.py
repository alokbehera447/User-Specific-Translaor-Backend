from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model_nllb = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def translate(text: str, source_lang: str, target_lang: str) -> str:
    tokenizer.src_lang = source_lang  # ✅ Set source language

    inputs = tokenizer(text, return_tensors="pt")

    translated_tokens = model_nllb.generate(
        **inputs,
        forced_bos_token_id=tokenizer.lang_code_to_id[target_lang]  # ✅ Target language
    )

    print("Step 2: Translation completed")
    return tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
