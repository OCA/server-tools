1/ _code_mask must be added in the related model e.g. in "gift.card":
_code_mask = {
"mask": "code_mask",
"template": "gift_card_tmpl_id"
}
2/ In the related model, You can change the code_mask value or use its default value (XXXXXX-00): x means a random lowercase letter, X means a random uppercase letter, 0 means a random digit.
3/ In addition, update a method of the target model to compute the code. For example the create method:
res = super().create(vals)
vals["code"] = res._generate_code()
