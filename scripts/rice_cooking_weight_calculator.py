RAW_RICE_GRAMS_PER_GO = 150
COOKED_RICE_GRAMS_PER_GO = 290

target_cooked_rice_grams = 600

required_rice_go = target_cooked_rice_grams / COOKED_RICE_GRAMS_PER_GO
required_raw_rice_grams = required_rice_go * RAW_RICE_GRAMS_PER_GO

print(f"{required_rice_go=:.2f}合")
print(f"{required_raw_rice_grams=:.0f}g")
