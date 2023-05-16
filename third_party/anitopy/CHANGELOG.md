# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Support 2K, 4K and 8K video resolutions.
- Add support to multi threading. This was not possible since the parsed tokens and elements where stored globally with the use of singletons.

### Fixed
- Increased the maximum amount of numbers to be considered as an episode from 3 to 4 since One Piece and Detective Conan have more than 999 episodes.
- In some cases a 0 was being parsed as the season number. For example, for the release group 0x539.
- An exception was being raised when the episode number was at the very end of the filename.

## [2.1.1] - 2022-07-24
### Fixed
- Fix a bug where the pattern `S<number>E<number>v<number>` was not being parsed correctly due to the version at the end.

## [2.1.0] - 2021-12-03
### Added
- Support for new keywords for audio and subtitles: DUAL-AUDIO, MULTIAUDIO, MULTI AUDIO, MULTI-AUDIO, MULTIPLE SUBTITLE, MULTI SUBS and MULTI-SUBS.

## [2.0.2] - 2021-11-14
### Fixed
- Parsing a filename containing the same anime type repeated once or more was causing a KeyError if this type was also parsed as a title.

## [2.0.1] - 2021-03-14
### Fixed
- Numbers not related to the episode number enclosed by brackets at the end of the filename caused an AttributeError while trying to parse one of the episode number patterns.

## [2.0.0] - 2019-03-19
### Changed
- The season pattern `S<number>` is now parsed and removed from the title.

## [1.3.0] - 2018-10-13
### Added
- Support TS video file extension keyword.

## [1.2.0] - 2018-08-16
### Added
- Support new keywords for audio, video and subtitles: EAC3, E-AC-3, Hardsubs, HEVC2, Hi444, Hi444P and Hi444PP.

### Fixed
- Add requirement for module enum34 for python below version 3.4.

## [1.1.0] - 2018-01-10
### Added
- Support to python 2 with absolute imports and unicode strings. Also use regex match instead of fullmatch.

## [1.0.1] - 2017-12-09
### Changed
- Options are now passed as a dictionary.

### Fixed
- Removed import loops between `parser_helper.py` and `parser_number.py`.

## [0.3.0] - 2017-09-29
### Added
- Identify some elements during tokenization. This cover some cases where some keywords are separated by uncommon delimiters or no delimiters at all creating tokens that doesn't match with any keyword.

### Fixed
- Remove accents from strings before trying to match it with a keyword.

## [0.2.0] - 2017-09-19
### Added
- Parse alternative episode numbers.

### Fixed
- Fix a bug where passing some special characters to the allowed delimiters may result in regex parsing strings incorrectly.
- Ignored strings option is now working.

## [0.1.1] - 2017-09-18
### Fixed
- Expose the `Options` class through the `__init__.py`.

## 0.1.0 - 2017-09-17
### Added
- Working parser for the majority of anime filenames.

[Unreleased]: https://github.com/igorcmoura/anitopy/compare/v2.1.1...HEAD
[2.1.1]: https://github.com/igorcmoura/anitopy/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/igorcmoura/anitopy/compare/v2.0.2...v2.1.0
[2.0.2]: https://github.com/igorcmoura/anitopy/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/igorcmoura/anitopy/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/igorcmoura/anitopy/compare/v1.3.0...v2.0.0
[1.3.0]: https://github.com/igorcmoura/anitopy/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/igorcmoura/anitopy/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/igorcmoura/anitopy/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/igorcmoura/anitopy/compare/v0.3.0...v1.0.1
[0.3.0]: https://github.com/igorcmoura/anitopy/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/igorcmoura/anitopy/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/igorcmoura/anitopy/compare/v0.1.0...v0.1.1
