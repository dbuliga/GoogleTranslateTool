

### Installation
Google Translation Tool requires [GCloud API](https://cloud.google.com/translate/docs/quickstart)
and `python3`.

### Implementation
`gtd` represents the actual daemon which listens for data on a translation queue 
defined at `localhost` using the port `4415`. When these two are provided by the 
`gtranslate` it reads the content of the file one by one and forms the internal 
data. This internal data is used as a payload for the request which detects in a 
single call all the languages from the provided file. Then it starts a new process 
for each line and does the translation from the detected language to the target 
language provided via `gtranslate`. 

Each translation is being performed via the GCloud rest API, same as the detection.

`gtranslate` is the way where the user can start a translation of a file by passing 
the following two arguments to it: 

- a given filename having on each line a text for the translation process
- target language to do the translation of the content of the previously given file

These two arguments are sent to the same queue to the `gtd` for the translation.

The number of requests per second can be limited by setting the environment variable
`QUERIES_PER_SEC` when starting the `gtd` (the default value is set at 10 request/sec).

### Usages

Starting the Google Translation daemon in one terminal with the following command 
```sh
$ QUERIES_PER_SEC=5 ./gtd.py
```

while in another terminal start the translation of the file `filename` with the target
language `en`
```sh
$ ./gtranslate.py -f filename -lang en
```

### Example

While testing with the content of the file `input_file`:
```json
Buna dimineata
Buona sera
Guten tag
Arrivederci
```

having the target language set as `en` we are getting as a response the following text translation:
```json
Good morning
Good evening
Good day
Goodbye
```
