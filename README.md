# General Setup

1. Change the variable PROJECT_DIR in line 13 of src/config.py to match the filepath to the root of your local project directory.
2. Edit the filepath listed under cfg['parser_params']['dictionary_dir'] on line 61 of src/config.py to match the dictionary directory of Mecab on your local machine.

    - For best results install the mecab-ipadic-neologd dictionary, which is [here](https://github.com/neologd/mecab-ipadic-neologd).
3. Run *src/config.py* as follows:
	```console
	python src/config.py
	```

# Usage

1. From the root directory, run the following command and follow the terminal prompts:
  ```console
  python gen_sentence_errors.py
  ```
2. Optionally, the following two flags can also be used:

  - *length_bias* - biases the output generated sentences to those with fewer or more errors. If the value of *length_bias* is greater than 0, sentences with fewer errors will be weighted more highly. If *length_bias* is less than 0, than sentences with more errors will be weighted more highly.
  - *n_show* - determines the number of candidate sentences to display per iteration