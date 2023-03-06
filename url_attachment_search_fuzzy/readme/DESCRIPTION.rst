This module creates a trigram index for the field url in ir_attachment in order to make
more efficient sql searches with like operand and this field.
In large dbs it can speed up a lot interface loading, for example when logging in.
