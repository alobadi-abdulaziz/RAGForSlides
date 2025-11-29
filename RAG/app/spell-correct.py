import pkg_resources
from symspellpy import SymSpell, Verbosity

sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=7)
input_term = "wht is th NLP"

# load dictionary file (English)
# sym_spell.load_dictionary(r"C:\Users\Azooz Alabadi\OneDrive\سطح المكتب\علوم الحاسب\انتروبي\me-Saleh\RAG\app\frequency_dictionary_en_82_765.txt", term_index=0, count_index=1)
# sym_spell.load_bigram_dictionary(r"C:\Users\Azooz Alabadi\OneDrive\سطح المكتب\علوم الحاسب\انتروبي\me-Saleh\RAG\app\frequency_bigramdictionary_en_243_342.txt", term_index=0, count_index=2)

suggestions = sym_spell.lookup(input_term, max_edit_distance=3)

for suggestion in suggestions:
    print(suggestion.term)