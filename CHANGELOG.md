# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Optional `image` input for image-conditioned generation requests.
- In-memory response cache keyed by `(image_name, image_size, prompt)`.
- Optional `image_name` input used in cache keying.

### Changed
- Node now skips API calls and returns cached output when the same `image_name`, image size, and `prompt` are provided.
