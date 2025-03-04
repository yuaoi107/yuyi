# Yuyi Project README

Yuyi is the RESTful API backend for a generic podcast hosting platform.

## Working Trace

### 2025-03-04

- [x] Initialize project
- [ ] Build database models
- [x] Build database functionality

[A Podcaster’s Guide to RSS - Apple](https://help.apple.com/itc/podcasts_connect/)

User:

- UserBase
    - username
    - nickname 
    - email
    - description
- User
    - id
    - hash_password
    - avatar_url
    - createtime
- UserUpload
- UserPublic
    - id
    - avatar_url
    - createtime

Podcast:

- Required:
    - title
    - description (str | CDATA)
    - itunes_image
    - language (iso639)
    - itunes_category
        - itunes_category
        - itunes_subcategory
    - itunes_explicit
- Recommended:
    - itunes_author
    - link
- Situational:
    - copyright
    - itunes_block (Yes | others)
    - itunes_complete (Yes | others)
    - generator

Episode:

- Required:
    - title
    - enclosure
        - url
        - length
        - type
    - guid
- Recommended:
    - pubDate (RFC 2822)
    - description (str | CDATA)
    - itunes_duration (seconds)
    - link
    - itunes_image
    - itunes_explicit (true | false)
- Situational:
    - itunes_episode
    - itunes_season
    - itunes_block