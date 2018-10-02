Go to *Technical Settings > Settings > Images* to configure all the images.
You can define images for specific objects, depending on the attributes and the company of the object.

The `selector` should return a boolean expression. All fields of the object are available to compute the result.

The system will first try to match an image with a company set up, then with the ones without a company.
If your object does not have a `company_id` field, this check will be ignored and only images without a company will be used.
