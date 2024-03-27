from google_spell_checker import GoogleSpellChecker

spell_checker = GoogleSpellChecker()
print(spell_checker.check("developmnet"))
# (False, 'development')
print(spell_checker.check("martialartz"))
# (False, 'martial arts')
print(spell_checker.check("amoxicillin-clavulanic"))
# (True, None)