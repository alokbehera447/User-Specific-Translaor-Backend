## MECAB

```bash

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/soumen/Job/ML-projects/xtts/locally/app.py", line 1, in <module>
    from TTS.api import TTS
  File "/home/soumen/.local/lib/python3.10/site-packages/TTS/api.py", line 12, in <module>
    from TTS.utils.synthesizer import Synthesizer
  File "/home/soumen/.local/lib/python3.10/site-packages/TTS/utils/synthesizer.py", line 11, in <module>
    from TTS.tts.configs.vits_config import VitsConfig
  File "/home/soumen/.local/lib/python3.10/site-packages/TTS/tts/configs/vits_config.py", line 5, in <module>
    from TTS.tts.models.vits import VitsArgs, VitsAudioConfig
  File "/home/soumen/.local/lib/python3.10/site-packages/TTS/tts/models/vits.py", line 33, in <module>
    from TTS.tts.utils.text.characters import BaseCharacters, BaseVocabulary, _characters, _pad, _phonemes, _punctuations
  File "/home/soumen/.local/lib/python3.10/site-packages/TTS/tts/utils/text/__init__.py", line 1, in <module>
    from TTS.tts.utils.text.tokenizer import TTSTokenizer
  File "/home/soumen/.local/lib/python3.10/site-packages/TTS/tts/utils/text/tokenizer.py", line 5, in <module>
    from TTS.tts.utils.text.phonemizers import DEF_LANG_TO_PHONEMIZER, get_phonemizer_by_name
  File "/home/soumen/.local/lib/python3.10/site-packages/TTS/tts/utils/text/phonemizers/__init__.py", line 10, in <module>
    from TTS.tts.utils.text.phonemizers.ja_jp_phonemizer import JA_JP_Phonemizer
  File "/home/soumen/.local/lib/python3.10/site-packages/TTS/tts/utils/text/phonemizers/ja_jp_phonemizer.py", line 3, in <module>
    from TTS.tts.utils.text.japanese.phonemizer import japanese_text_to_phonemes
  File "/home/soumen/.local/lib/python3.10/site-packages/TTS/tts/utils/text/japanese/phonemizer.py", line 355, in <module>
    _TAGGER = MeCab.Tagger()
  File "/home/soumen/.local/lib/python3.10/site-packages/MeCab/__init__.py", line 135, in __init__
    raise RuntimeError(error_info(rawargs)) from ee
RuntimeError:
----------------------------------------------------------

Failed initializing MeCab. Please see the README for possible solutions:

    https://github.com/SamuraiT/mecab-python3#common-issues

If you are still having trouble, please file an issue here, and include the
ERROR DETAILS below:

    https://github.com/SamuraiT/mecab-python3/issues

issueを英語で書く必要はありません。

------------------- ERROR DETAILS ------------------------
arguments:
[ifs] no such file or directory: /home/soumen/.local/lib/python3.10/site-packages/unidic/dicdir/mecabrc


```

This error occurs because MeCab cannot find the required dictionary files or configuration file (`mecabrc`) for Japanese text processing. Here's how to fix it:

### Solution:

1. **Install MeCab and Dictionaries**:
   First, make sure you have MeCab and the necessary dictionaries installed:

   ```bash
   sudo apt-get install mecab mecab-ipadic-utf8 libmecab-dev
   ```

2. **Install Unidic (if needed)**:
   The error suggests it's looking for Unidic dictionary. Install it with:

   ```bash
   pip install unidic
   python -m unidic download
   ```

3. **Set Environment Variable**:
   Tell MeCab where to find the dictionary:

   ```bash
   export MECABRC=/usr/local/etc/mecabrc
   ```

   Or if you're using Unidic:

   ```bash
   export MECABRC=/home/soumen/.local/lib/python3.10/site-packages/unidic/dicdir/mecabrc
   ```

4. **Verify Installation**:
   Test MeCab from command line:

   ```bash
   echo "テスト" | mecab
   ```

5. **Reinstall mecab-python3**:
   ```bash
   pip install --force-reinstall mecab-python3
   ```

### Alternative Solution:

If you don't specifically need Japanese processing, you might be able to disable it in your TTS configuration.

### Common Issues:

- The dictionary path might be different on your system. Check where `mecabrc` is actually located.
- If you're in a virtual environment, make sure all packages are installed within it.
- Some systems require additional symlinks from `/usr/local/etc/mecabrc` to `/etc/mecabrc`

pip3 install torch==2.1.0+cpu torchaudio==2.1.0+cpu torchvision==0.16.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip3 install torchmetrics==1.7.1 transformers==4.35.2 torch-audiomentations==0.12.0 torch_pitch_shift==1.2.5
pip3 install pyannote.audio==3.3.2
