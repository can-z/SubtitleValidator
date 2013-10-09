SubtitleValidator
=================

A validator for subtitle files used by YYeTS forum for translating English subtitles to Chinese.

TODO
----

- [x] English ellipsis --> WARNING
- [x] Ignore quotation marks at the end of sentences
- [x] Double spaces in Chinese captions
- [x] Single space in English captions
- [ ] Spaces before hyphens in English captions
- [ ] No space before hyphens in Chinese captions
- [x] Ignore hyphens at the beginning of English captions
- [ ] Auto-fix errors
- [x] Keep previous capitalization mode if an English line is empty
- [x] Ignore empty English lines
- [ ] If a Chinese/English line has hyphens for different characters, the other line must have them too
- [ ] Skip format error lines and process the rest
- [ ] Ignore cases for words such as "I"
- [ ] Fix English punctuation in Chinese lines
- [ ] Show "No Error" message if no error
- [ ] Show message for Exceptions
- [ ] Complete really_smart_decode()
- [ ] Better and Chinese system error messages

